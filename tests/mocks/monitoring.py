Set-Content -Path "tests/mocks/monitoring.py" -Value @"
class MockMonitor:
    class Metrics:
        pass

    def __getattr__(self, name):
        return self.Metrics

monitor = MockMonitor()
"@