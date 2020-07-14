import sqlite3 as sql
import os

class Database:
    """This class manages DB functionality - connecting, checking every table, inserting data, selecting and deleting."""
    @staticmethod
    def connect():
        """Connects to DB.

        Returns:
            instance: SQLite instance.

        """

        filename = "knihovna"

        # zda existuje soubor
        try:
            db = open(filename+".db", "r")
            db.close()
        # pokud soubor neexistuje
        except:
            # zda je soubor možné vytvořit
            try:
                db = open(filename+".db", "w+")
                db.close()
            # pokud není možné soubor vytvořit např. kvůli nedostatečným permissím
            except:
                return(None)

        os.chmod(filename+".db", 0o777)

        try:
            # připojení k DB
            db = sql.connect(filename+".db", check_same_thread=False, isolation_level=None)
        except:
            return(False)

        Database.checkTables(db)
        return(db)
    @staticmethod
    def checkTables(db):
        """Checks tables in DB.

        Args:
            db (instance): SQLite instance.

        Returns:
            Boolean: whether check was successful.

        """

        # nastavení kurzoru (můžeme pracovat s DB)
        cursor = db.cursor()

        # vytvoření tabulky logs
        try:
            cursor.execute("""CREATE TABLE logs (
            `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `logType` VARCHAR(30) NOT NULL,
            `logMessage` VARCHAR(75) NOT NULL,
            `date` DATE NOT NULL DEFAULT (datetime('now','localtime'))
            )""")
        except:
            pass
        else:
            Database.insertLog(["DB", "Vytvořena tabulka 'logs'"], db)

        # vytvoření tabulky bookWorkers
        try:
            cursor.execute("""CREATE TABLE bookWorkers (
            `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
            `bookID` INTEGER NOT NULL,
            `workersID` INTEGER NOT NULL
            )""")
        except:
            pass
        else:
            Database.insertLog(["DB", "Vytvořena tabulka 'bookWorkers'"], db)

        # vytvoření tabulky people
        try:
            cursor.execute("""CREATE TABLE people (
            `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
            `forename` VARCHAR(100) NOT NULL,
            `surname` VARCHAR(100) NOT NULL,
            `birthPlace` VARCHAR(100),
            `birthDate` date
            )""")
        except:
            pass
        else:
            Database.insertLog(["DB", "Vytvořena tabulka 'people'"], db)

        # vytvoření tabulky roles
        try:
            cursor.execute("""CREATE TABLE roles (
            `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
            `name` VARCHAR(50) UNIQUE NOT NULL
            )""")
        except:
            pass
        else:
            Database.insertLog(["DB", "Vytvořena tabulka 'roles'"], db)

        # základní hodnota 'author'
        try:
            cursor.execute("""INSERT INTO roles (name) VALUES ('author')""")
        except:
            pass
        else:
            Database.insertLog(["DB", "Do tabulky 'roles' byla vložena základní hodnota 'author'."], db)

        # základní hodnota 'illustrator'
        try:
            cursor.execute("""INSERT INTO roles (name) VALUES ('illustrator')""")
        except:
            pass
        else:
            Database.insertLog(["DB", "Do tabulky 'roles' byla vložena základní hodnota 'illustrator'."], db)

        # vytvoření tabulky workers
        try:
            cursor.execute("""CREATE TABLE workers (
            `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
            `peopleID` INTEGER NOT NULL,
            `roleID` INTEGER NOT NULL
            )""")
        except:
            pass
        else:
            Database.insertLog(["DB", "Vytvořena tabulka 'workers'"], db)

        # vytvoření tabulky books
        try:
            cursor.execute("""CREATE TABLE books (
            `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
            `title` VARCHAR(50) UNIQUE NOT NULL,
            `year` DATE NOT NULL
            )""")
        except:
            pass
        else:
            Database.insertLog(["DB", "Vytvořena tabulka 'books'"], db)

        # vytvoření tabulky roles
        try:
            cursor.execute("""CREATE TABLE roles (
            `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
            `name` VARCHAR(50) UNIQUE NOT NULL
            )""")
        except:
            pass
        else:
            Database.insertLog(["DB", "Vytvořena tabulka 'roles'"], db)

        # vytvoření tabulky users
        # try:
        #     cursor.execute("""CREATE TABLE users (
        #     `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
        #     `forename` VARCHAR(100) NOT NULL,
        #     `lastname` VARCHAR(100) NOT NULL,
        #     `telephoneNumber` INTEGER(20) NOT NULL
        #     )""")
        # except:
        #     pass
        # else:
        #     Database.insertLog(["DB", "Vytvořena tabulka 'users'"], db)

        # vytvoření tabulky rents
        # try:
        #     cursor.execute("""CREATE TABLE rents (
        #     `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
        #     `bookID` INTEGER NOT NULL,
        #     `userID` INTEGER NOT NULL
        #     )""")
        # except:
        #     pass
        # else:
        #     Database.insertLog(["DB", "Vytvořena tabulka 'rents'"], db)

        # vytvoření tabulky booksMeta
        try:
            cursor.execute("""CREATE TABLE booksMeta (
            `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
            `bookID` INTEGER NOT NULL,
            `metaKey` VARCHAR(100) NOT NULL,
            `metaValue` VARCHAR(100) NOT NULL
            )""")
        except:
            pass
        else:
            Database.insertLog(["DB", "Vytvořena tabulka 'booksMeta'"], db)

        cursor.close()

    @staticmethod
    def insertLog(data, db = None):
        """Inserts logs do database.

        Args:
            data (list): List that contains logType (DB, Info) and logMessage.
            db (instance; default None): SQLite instance; if is not passed, this method will try to connect on its own.

        Returns:
            Boolean: whether insert was successful or not.

        """

        if not db:
            db = Database.connect()
            # if db fails before insert
            if not db:
                return(False)

        cursor = db.cursor()

        cursor.execute("INSERT INTO logs ('logType', 'logMessage') VALUES (?, ?)", data)

        if not db:
            cursor.close()
            db.close()
        return(True)
    @staticmethod
    def select(sql):
        """Handles SELECTs.

        Args:
            sql (string): sql request.

        Returns:
            array: returns requested data.

        """
        if not sql:
            return False

        result = ""

        try:
            db = Database.connect()
            cursor = db.cursor()

            cursor.execute(sql)
            result = cursor.fetchall()


            cursor.close()
            db.close()
        except:
            pass
        finally:
            return(result)

    @staticmethod
    def execute(sql):
        """Executes commands that need commit.

        Args:
            sql (string): sql request.

        Returns:
            int: last commited ID, False if action is DELETE.

        """
        result = None
        if not sql:
            return False

        try:
            db = Database.connect()
            cursor = db.cursor()

            cursor.execute(sql)
            db.commit()
            try:
                result = cursor.lastrowid
            except:
                result = False


            cursor.close()
            db.close()
        except:
            pass
        finally:
            return(result)

# when you run this module independently
if __name__ == "__main__":
    help(Database)
