from app import create_app


def test_raw_html_generates_report():
    client = create_app().test_client()

    response = client.post("/analyze", data={"raw_html": '<title>Demo</title><button id="save">Save</button>'})

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Locator Lense" in body
    assert "Demo" in body
    assert "#save" in body


def test_both_inputs_are_rejected():
    client = create_app().test_client()

    response = client.post("/analyze", data={"url": "https://example.com", "raw_html": "<button>Save</button>"})

    assert response.status_code == 400
    assert "exactly one" in response.get_data(as_text=True)


def test_report_escapes_untrusted_html():
    client = create_app().test_client()

    response = client.post("/analyze", data={"raw_html": '<title>&lt;script&gt;alert(1)&lt;/script&gt;</title><button>Save</button>'})

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;" in body