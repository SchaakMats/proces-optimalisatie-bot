from app import slugify, parse_summary_response


def test_slugify_basic():
    assert slugify("Bouwbedrijf Van der Berg") == "bouwbedrijf_van_der_berg"


def test_slugify_special_chars():
    assert slugify("Bedrijf & Zonen B.V.") == "bedrijf_zonen_bv"


def test_slugify_strips_whitespace():
    assert slugify("  Test Bedrijf  ") == "test_bedrijf"


def test_slugify_multiple_spaces():
    assert slugify("Test  Bedrijf") == "test_bedrijf"


def test_parse_summary_valid_json():
    raw = '{"missing_fields": ["branche"], "intake_complete": false, "md_content": "# Test"}'
    result = parse_summary_response(raw)
    assert result["missing_fields"] == ["branche"]
    assert result["intake_complete"] is False
    assert result["md_content"] == "# Test"


def test_parse_summary_json_with_preamble():
    raw = 'Here is the result:\n{"missing_fields": [], "intake_complete": true, "md_content": "# Done"}'
    result = parse_summary_response(raw)
    assert result["intake_complete"] is True
    assert result["missing_fields"] == []


def test_parse_summary_invalid_json_returns_defaults():
    result = parse_summary_response("this is not json at all")
    assert "missing_fields" in result
    assert result["intake_complete"] is False
