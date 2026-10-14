from app.intelligence.categorizer import (
    BaselineCategorizer,
    CategorizationResult,
    get_categorizer,
)


def test_product_quality_categorization():
    categorizer = get_categorizer()
    res = categorizer.categorize("The device hardware has a broken battery and poor craftsmanship.")
    assert res.category == "Product Quality"
    assert res.confidence_score > 0.50


def test_customer_support_categorization():
    categorizer = get_categorizer()
    res = categorizer.categorize("The customer service agent on the support team was very rude and unhelpful.")
    assert res.category == "Customer Support"
    assert res.confidence_score > 0.50


def test_pricing_categorization():
    categorizer = get_categorizer()
    res = categorizer.categorize("The subscription renewal is way too expensive and not worth the cost.")
    assert res.category == "Pricing"
    assert res.confidence_score > 0.50


def test_delivery_categorization():
    categorizer = get_categorizer()
    res = categorizer.categorize("The carrier tracking shows our parcel shipment was delayed by a week.")
    assert res.category == "Delivery"
    assert res.confidence_score > 0.50


def test_user_experience_categorization():
    categorizer = get_categorizer()
    res = categorizer.categorize("The user interface and checkout flow is hard to navigate.")
    assert res.category == "User Experience"
    assert res.confidence_score > 0.50


def test_feature_request_categorization():
    categorizer = get_categorizer()
    res = categorizer.categorize("Please add dark mode support and an export option for invoices.")
    assert res.category == "Feature Request"
    assert res.confidence_score > 0.50


def test_ambiguous_feedback_falls_back_to_other():
    categorizer = get_categorizer()
    res = categorizer.categorize("Hello, today is Wednesday.")
    assert res.category == "Other"
    assert res.confidence_score <= 0.60
