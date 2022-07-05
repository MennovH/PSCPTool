import datetime as dt
import sys
import json
import pandas as pd
import html
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine

global host, schema, user, password, pay_day, sql_class
pay_day = 22
date = dt.date.today()
year_list = [year for year in range(date.year - 4, date.year + 2)]
month_list = ['', 'Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
host, schema, user, password = 'localhost', 'income', 'income', f'{"$KG3Z$yL2QtEdD&0Qw8nAKXFi883nek*" if sys.platform == "win32" else json.load(open("/home/pi/pw", "r"))["income"]}'


class SQL:
    def __init__(self, host=host, schema=schema, user=user, password=password):
        try:
            self.engine = create_engine(f'{"mysql+mysqlconnector" if sys.platform == "win32" else "mariadb+mariadbconnector"}://{user}:{password}@{host}/{schema}')
            self.get_criteria()
            self.get_users()
            self.status = 1
        except Exception as e:
            print(e)
            self.engine = ''
            self.status = 0


    def get_criteria(self):
        self.options = self.execute_query(['SELECT criterion FROM income.criteria'])


    def get_users(self):
        self.users = self.fetch_table('users')
        self.pay_day = self.users['pay_day'].to_list()
        self.users = self.users['email'].to_list()


    def execute_query_no_injection(self, query, parameters):
        conn = self.engine.connect()
        return conn.execute(query, parameters).fetchall()


    def execute_query(self, queries):
        if not isinstance(queries, list):
            queries = [queries]
        results = []
        if len(queries) > 1:
            for query in queries:
                try:
                    result = pd.read_sql_query(query, self.engine)
                    results.append(result)
                except:
                    continue
        elif len(queries) == 1:
            if isinstance(queries[0], tuple):
                    self.engine.connect().execute(queries[0])
            else:
                if queries[0][:6].lower() != 'select':
                    self.engine.connect().execute(queries[0])
                    return
                else:
                    return pd.read_sql_query(queries[0], self.engine)
        return results

    def fetch_table(self, table):
        try:
            return pd.read_sql_table(table, self.engine)
        except Exception as e:
            print(e)
            pass


sql_class = SQL()


class selection:
    def __init__(self, year, month, day, sel_user, sort=[], option=None):
        sql_class = SQL()
        sql_class.get_criteria()
        sql_class.get_users()

        pay_day = day
        sql = f"SELECT * FROM recurring WHERE user_id={sel_user};"
        df = sql_class.execute_query(sql)
        df['start_date'] = pd.to_datetime(df['start_date']).dt.date
        #month += 1 #nog aanpassen
        if option is None:
            df = df[(df.user_id == sel_user)]
            #month -= 1

            if month - 1 <= 0:
                self.m = 12
                self.y = year - 1
            else:
                self.m = month -1
                self.y = year
            #else:
            #    if month <= 0:
            #        self.m = 12
            #        self.y = year-1
            #    else:
            #        self.m = month
            #        self.y = year

            self.min_date = dt.date(self.y, self.m, pay_day)
            self.max_date = self.min_date + relativedelta(months=1) - relativedelta(days=1)
            id, onderwerp, bedrag, betaaldatum, status, criterium, users = [[] for _ in range(7)]
            sql = f"SELECT * FROM income.balance WHERE (pay_date BETWEEN '{self.min_date.strftime('%Y-%m-%d')}' AND '{self.max_date.strftime('%Y-%m-%d')}') AND user_id={sel_user}"
            self.balans = sql_class.execute_query(sql)
            self.balans['pay_date'] = pd.to_datetime(self.balans['pay_date'], format='%Y-%m-%d')

            for row in df.itertuples():
                s = 0
                m = self.m
                y = self.y
                f = row.recurrence
                d = row.start_date
                ed = row.end_date

                if str(ed) == 'None' or ed is None or str(ed) == 'NaT' or str(ed) == '':
                    ed = dt.date(2300,1,1)

                if ed < self.min_date:
                    continue

                try:
                    if self.min_date > dt.date(ed.year, ed.month, ed.day):
                        continue
                except:
                    pass
                if row[2] == 'Amvest Huur':
                    print(row[2])
                    print(row[3])
                    print(f'ed:{ed}')
                    print(f'self.min_date:{self.min_date}')
                    print(f'self.max_date:{self.max_date}')

                if row[7] == 0 or any(self.balans.subject == row[2]) or any(self.balans.subject == html.escape(row[2])):
                    continue

                if f == 0:
                    if self.min_date <= dt.date(d.year, d.month, d.day) <= self.max_date:
                        betaaldatum.append(dt.date(d.year, d.month, d.day))
                        s = 1
                elif f % 12 == 0:
                    # per year
                    if (relativedelta(d, dt.date(y, d.month, d.day)).years * -1) % int(f / 12) == 0:
                        if self.min_date <= dt.date(y, d.month, d.day) <= self.max_date:
                            betaaldatum.append(dt.date(y, d.month, d.day))
                            s = 1
                elif f == 1:
                    if dt.date(d.year, d.month, d.day) > self.max_date:
                        continue

                    # per month
                    if ed < self.max_date:
                        continue

                    if d.day >= pay_day:
                        if self.m > 12:
                            m = 1
                            y = self.y + 1
                        else:
                            y = self.y
                        betaaldatum.append(dt.date(y, m, d.day))
                    else:
                        if self.m + 1 > 12:
                            m = 0
                            y = self.y + 1
                        betaaldatum.append(dt.date(y, m + 1, d.day))
                    s = 1
                else:
                    while 1:
                        if self.min_date <= d <= self.max_date:
                            betaaldatum.append(dt.date(d.year, d.month, d.day))
                            s = 1
                            break
                        if (d + relativedelta(months=f)) > self.max_date:
                            break
                        d += relativedelta(months=f)
                if s:
                    onderwerp.append(row[2])
                    filtered = self.balans.query(f"subject == '{row[2]}' and pay_date >= '{self.min_date}' and pay_date <= '{self.max_date}'")
                    if len(filtered) > 0:
                        id.append(filtered['id'].iloc[0])
                        betaaldatum[-1] = filtered['pay_date'].iloc[0]
                        bedrag.append(filtered['amount'].iloc[0])
                        status.append(filtered['payed'].iloc[0])
                        criterium.append(filtered['criterion'].iloc[0])
                        users.append(filtered['user_id'].iloc[0])
                    else:
                        id.append('')
                        bedrag.append(row[3])
                        status.append(0)
                        criterium.append(row[7])
                        users.append(sel_user)

            if len(self.balans) > 0:
                id += self.balans['id'].to_list()
                onderwerp += self.balans['subject'].to_list()
                bedrag += self.balans['amount'].to_list()
                betaaldatum += self.balans['pay_date'].to_list()
                status += self.balans['payed'].to_list()
                criterium += self.balans['criterion'].to_list()
                users += [sql_class.users[i-1] for i in self.balans['user_id'].to_list()]
                try:
                    betaaldatum = [d.strptime(d.strftime('%y-%m-%d'), '%y-%m-%d') for d in betaaldatum]
                except:
                    pass

            self.periodiek = pd.DataFrame(
                list(
                    zip(
                        id,
                        onderwerp,
                        bedrag,
                        betaaldatum,
                        status,
                        criterium,
                        users
                    )
                ),
                columns=[
                    'id',
                    'subject',
                    'amount',
                    'pay_date',
                    'payed',
                    'criterion',
                    'user_id'
                ],
            )
            #print(self.periodiek)
            try:
                budget = self.periodiek.loc[self.periodiek['subject'] == 'Boodschappen budget', 'amount'].sum()
                if budget != 0:
                    groceries = self.periodiek.loc[self.periodiek['criterion'] == 'Boodschappen', 'amount'].sum() - budget
                    if groceries < budget:
                        budget = 0 #groceries
                    else:
                        budget -= groceries
                self.periodiek.loc[self.periodiek['subject'] == 'Boodschappen budget', 'amount'] = budget
                self.periodiek.loc[self.periodiek['subject'] == 'Boodschappen budget', 'payed'] = '-'
                budget_dt = min(self.periodiek.loc[self.periodiek['payed'] == 0, 'pay_date'].values)
                if len(str(budget_dt)) > 0:
                    self.periodiek.loc[self.periodiek['subject'] == 'Boodschappen budget', 'pay_date'] = budget_dt
            except:
                pass
#            self.periodiek = self.periodiek.sort_values(by=sort1, ascending=True if sort2 == '▲' else False)
            
           # print('ok1.6')
            self.periodiek['pay_date'] = pd.to_datetime(self.periodiek['pay_date']).dt.date
            #self.periodiek = self.periodiek.sort_values(by=sort1, ascending=True if sort2 == '▲' else False)
            self.periodiek.drop_duplicates(subset=['subject', 'pay_date'], inplace=True)
            self.periodiek['payed'].mask(self.periodiek['payed'] == 0, 'Nee' , inplace=True )
            self.periodiek['payed'].mask(self.periodiek['payed'] == 1, 'Ja' , inplace=True )
            #print(self.periodiek)
        else:
            onderwerp, bedrag, frequentie, startdatum, einddatum, criterium, users = [[] for _ in range(7)]

            for row in df.itertuples():
                print(row)
                onderwerp.append(row[1])
                bedrag.append(row[2])
                frequentie.append(f'{row[3]} m')
                startdatum.append(row[4])
                einddatum.append(row[5] if str(row[5]) == 'NaT' else row[5].date())
                criterium.append(row[6])
                users.append(sql_class.users[row[7]-1])

            self.periodiek = pd.DataFrame(
                list(
                    zip(
                        onderwerp,
                        bedrag,
                        frequentie,
                        startdatum,
                        einddatum,
                        criterium,
                        users
                    )
                ),
                columns=[
                    'subject',
                    'amount',
                    'recurrence',
                    'start_date',
                    'end_date',
                    'criterion',
                    'user_id'
                ],
            )
            try:
                budget = self.periodiek.loc[self.periodiek['subject'] == 'Boodschappen budget', 'amount'].sum()
                if budget != 0:
                    groceries = self.periodiek.loc[self.periodiek['criterion'] == 'Boodschappen', 'amount'].sum()
                    if groceries < budget:
                        budget = 0 #groceries
                else:
                    budget -= groceries
                self.periodiek.loc[self.periodiek['subject'] == 'Boodschappen budget', 'amount'] = budget
                self.periodiek.loc[self.periodiek['subject'] == 'Boodschappen budget', 'payed'] = '-'
                budget_dt = self.periodiek.loc[self.periodiek['payed'] == 0, 'pay_date'].values[0]
                if len(str(budget_dt)) > 0:
                    self.periodiek.loc[self.periodiek['subject'] == 'Boodschappen budget', 'pay_date'] = budget_dt
            except:
                pass
        #return self.periodiek
        self.periodiek = self.periodiek.sort_values(by=sort[0], ascending=sort[1])
#        self.periodiek = self.periodiek.sort_values(by=sort[0], ascending=1 if sort[1] == 'asc' else 0)
