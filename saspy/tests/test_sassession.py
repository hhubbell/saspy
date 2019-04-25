import unittest
import saspy
import collections
import os
import tempfile


class TestSASsessionObject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sas = saspy.SASsession()
        cls.sas.set_batch(True)

        cls.tempdir = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.sas._endsas()
        cls.tempdir.cleanup()

    def test_sassession(self):
        self.assertIsInstance(self.sas, saspy.SASsession)

    def test_sassession_exist_true(self):
        """
        Test method exist returns True for a dataset that exists
        """
        exists = self.sas.exist('cars', libref='sashelp')
        self.assertTrue(exists)

    def test_sassession_exist_false(self):
        """
        Test method exist returns False for a dataset that does not exist
        """
        exists = self.sas.exist('notable', libref='sashelp')
        self.assertFalse(exists)

    def test_sassession_csv_read(self):
        """
        Test method read_csv properly imports a csv file
        """
        EXPECTED = ['1', 'Acura', 'MDX', 'SUV', 'Asia', 'All', '$36,945', '$33,337', '3.5']

        fname = os.path.join(self.sas.workpath, 'sas_csv_test.csv')
        self.sas.write_csv(fname, 'cars', libref='sashelp')

        csvdata = self.sas.read_csv(fname, 'csvcars', results='text')

        ll = csvdata.head()

        rows = ll['LST'].splitlines()
        retrieved = [x.split() for x in rows]

        self.assertIn(EXPECTED, retrieved, msg="csvcars.head() result didn't contain row 1")

    def test_sassession_csv_write(self):
        """
        Test method write_csv properly exports a csv file
        """
        fname = os.path.join(self.sas.workpath, 'sas_csv_test.csv')
        log = self.sas.write_csv(fname, 'cars', libref='sashelp')

        self.assertNotIn("ERROR", log, msg="sas.write_csv() failed")

    def test_sassession_upload(self):
        """
        Test method upload properly uploads a file
        """
        local_file = os.path.join(self.tempdir.name, 'simple_csv.csv')
        remote_file = self.sas.workpath + 'simple_csv.csv'

        with open(local_file, 'w') as f:
            f.write("""A,B,C,D\n1,2,3,4\n5,6,7,8""")

        self.sas.upload(local_file, remote_file)

        # `assertTrue` fails on empty dict or None, which is returned
        # by `file_info`
        self.assertTrue(self.sas.file_info(remote_file))

    def test_sassession_download(self):
        """
        Test method download properly downloads a file
        """
        local_file_1 = os.path.join(self.tempdir.name, 'simple_csv.csv')
        local_file_2 = os.path.join(self.tempdir.name, 'simple_csv_2.csv')
        remote_file = self.sas.workpath + 'simple_csv.csv'

        with open(local_file_1, 'w') as f:
            f.write("""A,B,C,D\n1,2,3,4\n5,6,7,8""")

        self.sas.upload(local_file_1, remote_file)
        self.sas.download(local_file_2, remote_file)

        self.assertTrue(os.path.exists(local_file_2))

    def test_sassession_datasets_work(self):
        """
        Test method datasets can identify that the WORK library exists
        """
        EXPECTED = ['Libref', 'WORK']

        log = self.sas.datasets()
        rows = log.splitlines()
        retrieved = [x.split() for x in rows]

        self.assertIn(EXPECTED, retrieved)

    def test_sassession_datasets_sashelp(self):
        """
        Test method datasets can identify that the SASHELP library exists
        """
        EXPECTED = ['Libref', 'SASHELP']

        log = self.sas.datasets('sashelp')
        rows = log.splitlines()
        retrieved = [x.split() for x in rows]

        self.assertIn(EXPECTED, retrieved)

    def test_sassession_hasstat(self):
        """
        Test method sasstat() returns a SASstat object.
        """
        stat = self.sas.sasstat()

        self.assertIsInstance(stat, saspy.sasstat.SASstat, msg="stat = self.sas.sasstat() failed")

    def test_sassession_hasets(self):
        """
        Test method sasets() returns a SASets object.
        """
        ets = self.sas.sasets()

        self.assertIsInstance(ets, saspy.sasets.SASets, msg="ets = self.sas.sasets() failed")

    def test_sassession_hasqc(self):
        """
        Test method sasqc() returns a SASqc object.
        """
        qc = self.sas.sasqc()

        self.assertIsInstance(qc, saspy.sasqc.SASqc, msg="qc = self.sas.sasqc() failed")

    def test_sassession_hasml(self):
        """
        Test method sasml() returns a SASml object.
        """
        ml = self.sas.sasml()

        self.assertIsInstance(ml, saspy.sasml.SASml, msg="ml = self.sas.sasml() failed")

    def test_sassession_hasutil(self):
        """
        Test method sasutil() returns a SASutil object.
        """
        util = self.sas.sasutil()

        self.assertIsInstance(util, saspy.sasutil.SASutil, msg="util = self.sas.sasutil() failed")

    def test_sassession_dsopts_where_str(self):
        """
        Test method _dsopts properly supports `where` as a string.
        """
        EXPECTED = "where=(msrp < 20000 and make = 'Ford'"
        OPTDICT = {'where': "msrp < 20000 and make = 'Ford'"}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_dsopts_where_list(self):
        """
        Test method _dsopts properly supports `where` as a list.
        """
        EXPECTED = "where=(msrp < 20000 and make = 'Ford'"
        OPTDICT = {'where': "msrp < 20000", "make = 'Ford'"}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_dsopts_keep_str(self):
        """
        Test method _dsopts properly supports `keep` as a string.
        """
        EXPECTED = "keep=msrp enginsize cylinders horsepower"
        OPTDICT = {'keep': 'msrp enginesize cylinders horsepower'}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_dsopts_keep_list(self):
        """
        Test method _dsopts properly supports `keep` as a list.
        """
        EXPECTED = "keep=msrp enginsize cylinders horsepower"
        OPTDICT = {'keep': ['msrp', 'enginesize', 'cylinders', 'horsepower']}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_dsopts_drop_str(self):
        """
        Test method _dsopts properly supports `drop` as a string.
        """
        EXPECTED = "drop=msrp enginsize cylinders horsepower"
        OPTDICT = {'drop': 'msrp enginesize cylinders horsepower'}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_dsopts_drop_list(self):
        """
        Test method _dsopts properly supports `drop` as a list.
        """
        EXPECTED = "drop=msrp enginsize cylinders horsepower"
        OPTDICT = {'drop': ['msrp', 'enginesize', 'cylinders', 'horsepower']}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_dsopts_obs(self):
        """
        Test method _dsopts properly supports `obs` as an integer.
        """
        EXPECTED = "obs=10"
        OPTDICT = {'obs': 10}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_dsopts_firstobs(self):
        """
        Test method _dsopts properly supports `firstobs` as an integer.
        """
        EXPECTED = "firstobs=12"
        OPTDICT = {'firstobs': 12}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_dsopts_format_str(self):
        """
        Test method _dsopts properly supports `format` when it is the only
        dict key and its type is a string.
        """
        EXPECTED = ";\n\tformat msrp dollar10.2;"
        OPTDICT = {'format': 'msrp dollar10.2'}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_dsopts_format_dict(self):
        """
        Test method _dsopts properly supports `format` when it is the only
        dict key and its type is a dict.
        """
        EXPECTED = ";\n\tformat msrp dollar10.2;"
        OPTDICT = {'format': {'msrp': 'dollar10.2'}}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_dsopts_format_combined(self):
        """
        Test method _dsopts properly supports `format` when it is combined
        with other arguments.
        """
        EXPECTED = "where=(msrp < 20000) keep=msrp horsepower;\n\tformat msrp dollar10.2;"
        # NOTE: Use OrderedDict here to support testing on Python < 3.6
        OPTDICT = collections.OrderedDict([
            ('where', 'msrp < 20000'),
            ('keep', ['msrp', 'horsepower']),
            ('format', {'msrp': 'dollar10.2'})])

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_impopts_datarow(self):
        """
        Test method _impopts properly supports `datarow`.
        """
        EXPECTED = "datarow=2;"
        OPTDICT = {'datarow': 2}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_impopts_delimiter(self):
        """
        Test method _impopts properly supports `delimiter`.
        """
        EXPECTED = "delimiter='2c'x;"
        OPTDICT = {'delimiter': ','}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_impopts_getnames(self):
        """
        Test method _impopts properly supports `getnames`.
        """
        EXPECTED = "getnames=YES;"
        OPTDICT = {'getnames': True}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_impopts_guessingrows(self):
        """
        Test method _impopts properly supports `guessingrows`.
        """
        EXPECTED = "guessingrows=100;"
        OPTDICT = {'guessingrows': 100}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_expopts_delimiter(self):
        """
        Test method _expopts properly supports `delimiter`.
        """
        EXPECTED = "delimiter='2c'x;"
        OPTDICT = {'delimiter': ','}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))

    def test_sassession_expopts_putnames(self):
        """
        Test method _expopts properly supports `putnames`.
        """
        EXPECTED = "putnames=NO;"
        OPTDICT = {'putnames': False}

        self.assertEqual(EXPECTED, self.sas._dsopts(OPTDICT))
