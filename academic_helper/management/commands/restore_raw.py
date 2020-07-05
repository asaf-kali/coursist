from typing import List

from django.core import management
from django.core.management import BaseCommand
from django.db import connection
from tqdm.auto import tqdm, trange

from academic_helper.utils.logger import log


def concat(queries: List[str]) -> List[str]:
    result = []
    current = ""
    for query in queries:
        current += query
        if ";\n" in current:
            result.append(current)
            current = ""
    return result


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.queries: List[str] = []

    def add_arguments(self, parser):
        parser.add_argument("dump_path", type=str)

    def read_from_file(self, path: str):
        with open(path, encoding="utf-8") as file:
            queries = file.readlines()
        self.queries = concat(queries)

    def execute_all_queries(self) -> int:
        fail_count = 0
        with connection.cursor() as cursor:
            for i, query in enumerate(tqdm(self.queries, desc="Execution")):
                query = query.strip()
                try:
                    cursor.execute(query)
                except Exception as e:
                    fail_count += 1
                    # if "CREATE UNIQUE INDEX" in str(e):
                    #     continue
                    # if "CREATE INDEX" in str(e):
                    #     continue
                    # if "already exists" in str(e):
                    #     continue
                    # if "UNIQUE constraint failed" in str(e):
                    #     continue
                    # log.error(f"Query {i} failed: {e}: {query}")
                # else:
                #     if "CREATE TABLE" in query:
                #         continue
                #     if "CREATE INDEX" in query:
                #         continue
                #     log.info(query)
        return fail_count

    def handle(self, *args, **options):
        management.call_command("migrate")
        self.read_from_file(options["dump_path"])
        for i in range(10):
            print(f"Iteration {i + 1}")
            fail_count = self.execute_all_queries()
            if fail_count != 0:
                log.error(f"Fail count: {fail_count}")
