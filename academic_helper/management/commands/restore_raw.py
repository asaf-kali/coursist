import re
from time import sleep
from typing import List

from django.core import management
from django.core.management import BaseCommand
from django.db import connection
from tqdm.auto import tqdm

from academic_helper.utils.logger import log, wrap


def concat(queries: List[str]) -> List[str]:
    result = []
    current = ""
    for query in queries:
        current += query
        if ";\n" in current:
            result.append(current)
            current = ""
    return result


insert_re = re.compile(r"INSERT INTO \"(.*)\" VALUES\((.*)\);\s*")


def reconstruct_insert(query: str) -> str:
    result = insert_re.search(query)
    if not result:
        return ""
    table = result.group(1)
    values = result.group(2)
    return f"INSERT INTO {table} VALUES ({values});"


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.queries: List[str] = []

    def add_arguments(self, parser):
        parser.add_argument("dump_path", type=str)

    def read_from_file(self, path: str):
        with open(path, encoding="utf-8") as file:
            queries = file.readlines()
        queries = concat(queries)
        queries = filter(lambda query: "INSERT INTO" in query, queries)
        queries = list(map(lambda query: reconstruct_insert(query), queries))
        self.queries = queries

    def execute_all_queries(self) -> List[str]:
        failing = []
        _tqdm = tqdm(self.queries, desc="Execution")
        with connection.cursor() as cursor:
            for i, query in enumerate(_tqdm):
                query = query.strip()
                try:
                    cursor.execute(query)
                except Exception as e:
                    failing.append(query)
        sleep(1)
        _tqdm.clear()
        _tqdm.close()
        return failing

    def handle(self, *args, **options):
        management.call_command("migrate")
        self.read_from_file(options["dump_path"])
        failing = []
        last_count = 0
        fail_count = None
        i = 1
        while fail_count != last_count:
            print(f"\n\nIteration {i}")
            last_count = fail_count
            failing = self.execute_all_queries()
            fail_count = len(failing)
            if fail_count > 0:
                log.warning(f"Fail count: {wrap(fail_count)}, which is ~{100 * fail_count / len(self.queries):.0f}%")
            i += 1
        log.info(f"Converged. Failing queries:")
        for failed in failing:
            log.warning(failed)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_session;")
