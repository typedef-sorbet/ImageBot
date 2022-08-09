import sqlite3
import os
import traceback

_db_path = os.path.normpath(os.path.join(os.getcwd(), "stats.db"))

sqlite3.register_adapter(bool, int)
sqlite3.register_converter('BOOLEAN', lambda v: bool(int(v)))
sqlite3.register_converter('boolean', lambda v: bool(int(v)))

# God, I hate Python.
_SUBQUERIES_IGNORE = [
    tuple(["the"]),
    tuple(["a"]),
    tuple(["an"]),
    tuple(["and"]),
    tuple(["for"])
]

def get_db_conn():
    if not os.path.exists(_db_path):
        return None, f"Database file does not exist: {_db_path}"
    
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row

    return conn, None

def configure_db(conn):
    # What all do we want to track?
    # List of the following:
    # User name
    # User ID
    # search term
    # search result
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS SearchQueries(
            id              INTEGER PRIMARY KEY ASC,
            user_name       varchar(255),
            user_id         integer,
            search_term     varchar(255),
            search_result   varchar(1024)
        );
    ''')

    conn.commit()
    conn.close()

def log_search(user_name, user_id, search_term, search_result):
    conn, _ = get_db_conn()

    conn.execute('''
        INSERT INTO SearchQueries(user_name, user_id, search_term, search_result)
        VALUES (?, ?, ?, ?);
    ''', (user_name, user_id, search_term, search_result))

    conn.commit()
    conn.close()

def get_user_leaderboard(user_id = "", user_name = ""):
    # Count all of `user_id`s searches, and show the top 5.
    conn, _ = get_db_conn()

    res = None

    if user_id:
        res = conn.execute('''
            SELECT search_term, count(*) as cnt
            FROM SearchQueries
            WHERE user_id = :user_id
            GROUP BY search_term
            ORDER BY cnt DESC;
        ''', {"user_id": user_id}).fetchall()
    elif user_name:
        res = conn.execute('''
            SELECT search_term, count(*) as cnt
            FROM SearchQueries
            WHERE user_name = :user_name
            GROUP BY search_term
            ORDER BY cnt DESC;
        ''', {"user_name": user_name}).fetchall()
    else:
        print("Neither option given")

    # Res is a list of Row objects
    # Let's format it.

    return [
        {"search_term": row[0], 
        "count": row[1]}
        for row in res
    ]

def get_user_most_used_terms(user_name):
    conn, _ = get_db_conn()

    rows = conn.execute('''
        SELECT search_term
        FROM SearchQueries
        WHERE user_name = :user_name
    ''', {"user_name": user_name}).fetchall()

    # Keyed on tuples of word combinations
    # Value is count
    terms_dict = {}

    # Yes, this is incredibly inefficient. Too bad!
    for query in rows:
        split_query = query[0].lower().split()
        # God, I love Python.
        subqueries = [
            split_query[start:end]
            for start in range(len(split_query))
            for end in range(start, len(split_query))
            if start != end
        ]

        for subquery in subqueries:
            subquery = tuple(subquery)
            if subquery in _SUBQUERIES_IGNORE:
                continue
            if subquery not in terms_dict:
                terms_dict[subquery] = 0
            terms_dict[subquery] += 1

    return [
        {
            "search_term": " ".join(subquery),
            "count": terms_dict[subquery]
        }
        for subquery in sorted(terms_dict, key=terms_dict.get, reverse=True)[:5]
    ]

def get_server_most_used_terms():
    conn, _ = get_db_conn()

    rows = conn.execute('''
        SELECT search_term
        FROM SearchQueries
    ''').fetchall()

    # Keyed on tuples of word combinations
    # Value is count
    terms_dict = {}

    # Yes, this is incredibly inefficient. Too bad!
    for query in rows:
        split_query = query[0].lower().split()
        # God, I love Python.
        subqueries = [
            split_query[start:end]
            for start in range(len(split_query))
            for end in range(start, len(split_query))
            if start != end
        ]

        for subquery in subqueries:
            subquery = tuple(subquery)
            if subquery in _SUBQUERIES_IGNORE:
                continue
            if subquery not in terms_dict:
                terms_dict[subquery] = 0
            terms_dict[subquery] += 1

    return [
        {
            "search_term": " ".join(subquery),
            "count": terms_dict[subquery]
        }
        for subquery in sorted(terms_dict, key=terms_dict.get, reverse=True)[:5]
    ]

def get_term_leaderboard(search_term):
    pass

try:
    conn, reason = get_db_conn()
    configure_db(conn)
except Exception:
    print("Unable to configure database on startup:")
    print(reason)
    print(traceback.format_exc())
