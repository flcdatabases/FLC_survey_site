from datetime import datetime
from dateutil import relativedelta

"""
File Name: Simple.py
Author: Bryan Insfran
Description: Class meant to simplify the use
of sqlite3 by creating methods for that run
the sqlite commands in a neater manner

Warning: Must pass all parameters as strings
Example: self.insert('table_name', 'values')
"""

class Simplify():
    def __init__(self):
        self.__connection = "sqlitecloud://ccd05tfthz.g1.sqlite.cloud:8860/Testing?apikey=Mji9QZnn0DLv8by9woBTc105GxkTltAVbcixpOF71Cg"

    def test_connection(self):
        return self.__connection

    # Creates a table with the given name
    # Can take any number of varible arguments
    def create_table(self, name, *vars):
        initial = ('''CREATE TABLE ''' + name + ''' (''')
        
        temp = 0

        for var in vars:
            if temp == 0:
                initial += var
                temp += 1
                continue
            initial += (''', ''')
            initial += var

        initial += ''');'''

        return initial

    # Deletes given table if it already exists
    def remove_table(self, table):
        return('''DROP TABLE IF EXISTS ''' + table)

    # Similar to create_table inserts into given table
    # Can take any number of values (should be the amount of "columns" in a table)
    def insert(self, table, *values):
        formatted_values = []

        for value in values:
            if isinstance(value, str):
                formatted_values.append(f"'{value}'")  # Wrap strings in single quotes
            else:
                formatted_values.append(str(value))  # Convert non-strings to strings

        values_str = ", ".join(formatted_values)

        return ('''INSERT INTO ''' + table + ''' VALUES (''' + values_str + ''')''')

    # Returns all values in given table if no condition is given, condition is optional
    # Condition arugment runs on comparison operators (=, >=, <=, !=, LIKE, NOT, etc.)
    def search_all(self, table, condition=None):
        if condition == None:
            return ('''SELECT * FROM ''' + table)
        return ('''SELECT * FROM ''' + table + ''' WHERE ''' + condition)

    def search_vars(self, table, *vars):
        initial = '''SELECT '''
        
        temp = 0

        for var in vars:
            if temp == 0:
                initial += var
                temp += 1
                continue
            initial += (''',''')
            initial += var

        initial += ''' FROM '''
        initial += table

        return initial
    
    # Ordered by ASC or DESC
    # Order_var correspondes to a column
    def ordered_search(self, table, order_var, order='ASC', *vars):
        found = self.search_vars(table, *vars)
        
        found += ''' ORDER BY '''
        found += (order_var + ''' ''')
        found += order

        return found

    # Deletes any entry that matches given condition
    def remove(self, table, condition=None):
        if condition == None:
            return ('''DELETE from ''' + table)
        return ('''DELETE from ''' + table + ''' WHERE ''' + condition)
    
    def update_vars(self, table, condition=None, *vars):
        temp = 0

        for var in vars:
            if temp == 0:
                vari = var
                temp += 1
                continue
            vari += (''', ''')
            vari += var

        if condition == None:
            return ('''UPDATE ''' + table + ''' SET ''' + vari)
        return ('''UPDATE ''' + table + ''' SET ''' + vari + ''' WHERE ''' + condition)
    
    def multiples(self, table, col):
        return (f"SELECT {col}, COUNT(*) FROM {table} GROUP BY {col}")
        #return ('''SELECT ''' + col + ''',COUNT(*) FROM TABLE ''' + table + ''' GROUP BY ''' + col)

    def multiples_yes_var(self, table, col):
        return (f"SELECT COUNT({col}) FROM {table} WHERE TRIM({col})='Yes' GROUP BY {col}")

    def getColumn(self, table, data, cursor):
			# Arguments: table (A table of the database), data (a column), cursor (new cursor for every use of this function)
			# Returns: List of possible entries, amount of each entry found
            cursor.execute(self.multiples(table,data))
            column = cursor.fetchall()
		
            column_data=[]
            column_data_quantity=[]		
            for row in column:
                #if row[0] == '' or row[0] == None:
                    #pass
                    #column_data.append("N/A")
                    #column_data_quantity.append(row[-1])
                if row[0] != '' and row[0] != None:
                    column_data.append(row[0])
                    column_data_quantity.append(row[-1])

            return column_data, column_data_quantity
    
    def getColumnYes(self, table, data, cursor, destination):
			# Arguments: table (A table of the database), data (a column), cursor (new cursor for every use of this function), destination (place data is put into)
			# Returns: List of possible entries, amount of each entry found
            cursor.execute(self.multiples_yes_var(table, data))
            column = cursor.fetchall()
            if column != []:
                value = int(column[0][0])

                destination[0].append(data)
                destination[1].append(value)

                return data, value
            return None, None
    
    def getYears(self, cursor1, cursor2):
        # Arguments: cursor1 (corresponds to birth dates), cursor2 (corresponds to submission dates)
        # Returns: A list containing every year value submitted, and a list containing every count for the respective years
        # Additional note: This code currently only works for the General_info survey, which is why the table is not an input.

        birth_data = cursor1.execute("SELECT Date_Of_Birth FROM General_Information").fetchall()
        date_data = cursor2.execute("SELECT TIME_SUBMITTED FROM General_Information").fetchall()
        years = []
        counts = []
        for i in range(0, (min(len(birth_data), len(date_data)))):

                if birth_data[i] != "N/A" and date_data[i] != "N/A":
                    # Convert to strings
                    birth_convert = str(birth_data[i])
                    birth_convert = birth_convert[2:(len(birth_convert)-3)]
                    date_convert = str(date_data[i])
                    date_convert = date_convert[2:(len(date_convert)-3)]

                    # Convert to date format
                    birth_date = datetime.strptime(birth_convert, "%Y-%m-%d")
                    sub_date = datetime.strptime(date_convert, "%Y-%m-%d")

                    # Get difference in years
                    delta = relativedelta.relativedelta(sub_date, birth_date)

                    # Check for duplicates
                    if delta.years not in years:
                        years.append(delta.years)
                        counts.append(0)

                    # Add to count
                    year_index = years.index(delta.years)
                    counts[year_index] += 1


        #print(years)
        #print(counts)
        sorted_pairs = sorted(zip(years, counts))
        years_sorted = [v1 for v1, v2 in sorted_pairs]
        counts_sorted = [v2 for v1, v2 in sorted_pairs]
        #print(years_sorted)
        #print(counts_sorted)

        return years_sorted, counts_sorted