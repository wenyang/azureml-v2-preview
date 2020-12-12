# noxfile.py
import nox


@nox.session(python=["3.8", "3.7", "3.6"])
def tests(session):
    args = session.posargs or ["./tests/azure-ml/unittests/"]
    session.run("python", "./scripts/run_coverage_tests.py", "-p", "azure.ml", "-t", *args)
    session.run("coverage", "report")


@nox.session(python=["3.8", "3.7", "3.6"])
def mypy(session):
    session.run("python", "./scripts/run_mypy.py", "-s", "src/azure-ml/azure/")
