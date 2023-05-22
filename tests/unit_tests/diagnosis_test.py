import unittest

from flamapy.core.discover import DiscoverMetamodels  # This loads the tool in the python execution environment


# result = dm.use_operation_from_file("Glucose3FastDiag", "./smartwatch_inconsistent.fide", configuration_file="./pizzas_nonvalid.csvconf") # This launch the operation and stores the result on the result variable
# result = dm.use_operation_from_file("Glucose3FastDiag", "./smartwatch_inconsistent.fide") # This launch the operation and stores the result on the result variable
# print(result) # to print the result

class MyTestCase(unittest.TestCase):
    def test1(self):
        dm = DiscoverMetamodels()  # Instantiate the class
        result = dm.use_operation_from_file("Glucose3FastDiag", "../resources/smartwatch_inconsistent.fide")
        print(result)
        result = dm.use_operation_from_file("Glucose3FastDiag", "../resources/smartwatch_consistent.fide")
        print(result)

    def test_fastdiag(self):
        dm = DiscoverMetamodels()  # Instantiate the class
        result = dm.use_operation_from_file("Glucose3FastDiag", "../resources/smartwatch_inconsistent.fide")
        print(result)

    def test_quickxplain(self):
        dm = DiscoverMetamodels()  # Instantiate the class
        result = dm.use_operation_from_file("Glucose3QuickXPlain", "../resources/smartwatch_inconsistent.fide")
        print(result)


if __name__ == '__main__':
    unittest.main()
