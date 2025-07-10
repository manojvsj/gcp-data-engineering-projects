# main.py
import functions_framework
from dq_check import run_dq_checks

@functions_framework.http
def main(request):
    run_dq_checks()
    return "Data quality checks completed."