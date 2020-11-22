all_health_checks = []

class HealthCheckResult:
    def __init__(self):
        self.errors = []
        self.warnings = []

def health_check(title):
    class HealthCheck:
        def __init__(self, func):
            self.func = func
            self.title = title
            all_health_checks.append(self)

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)
        
    return HealthCheck

def run_health_checks(debug=False):
    result = HealthCheckResult()
    print('==================================================================')
    print('List of health checks:')
    for index, hc in enumerate(all_health_checks):
        print("{} : {}".format(index + 1, hc.title))
    print('------------------------------------------------------------------')
    print("Running health checks ...")
    for index, hc in enumerate(all_health_checks):
        hc(result, debug)
    print('------------------------------------------------------------------')
    if result.errors:
        print("Running health checks complete with errors")
    elif result.warings:
        print("Running health checks complete with warning")
    else:
        print("Running health checks successful")
    for e in result.errors:
        print(" ERROR: {}".format(e))
    for w in result.warnings:
        print(" WARNING: {}".format(w))
    print('==================================================================')

    if result.errors:
        exit(1)
    else:
        exit(0)
