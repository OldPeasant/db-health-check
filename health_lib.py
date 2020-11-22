all_health_checks = []

def health_check(title):
    class HealthCheck:
        def __init__(self, func):
            self.func = func
            self.title = title
            all_health_checks.append(self)

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)
        
    return HealthCheck

def run_health_checks():
    print('==================================================================')
    print('List of health checks:')
    for index, hc in enumerate(all_health_checks):
        print("{} : {}".format(index + 1, hc.title))
    print('------------------------------------------------------------------')
    print("Running health checks ...")
    failures = []
    for index, hc in enumerate(all_health_checks):
        success = hc()
        print("  Running health check {}: {}".format(index + 1, "Success" if success else "Failure"))
        if not success:
            failures.append(hc)
    print('------------------------------------------------------------------')
    print("Running health checks completed")
    if len(failures) > 0:
        print("The following checks failed:")
        for hc in failures:
            print("  {}".format(hc.title))
        print('==================================================================')
        exit(1)
    else:
        print("All checks successful")
        print('==================================================================')
        exit(0)
