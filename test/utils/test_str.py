from utils.str import md5


def test_md5_hash_matches_known_value():
    expected = "900150983cd24fb0d6963f7d28e17f72"
    assert md5("abc") == expected
