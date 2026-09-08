from app.services.redaction import redact

def test_redaction():
    text='password=secret token=abc Authorization: Bearer XYZ'
    out=redact(text)
    assert 'secret' not in out
    assert 'abc' not in out
    assert 'XYZ' not in out

def test_plain_text():
    assert redact('hello world') == 'hello world'
