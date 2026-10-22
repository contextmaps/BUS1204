"""Pricing rules and quote generator for Foxglove Inn."""

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP


BASE_RATES = {
    "Queen Room": Decimal("139"),
    "King Room": Decimal("159"),
    "Two-Room Suite": Decimal("249"),
}
WHOLE_CURRENCY_CODES = {"JPY", "KRW", "HUF", "ISK"}


def _parse_date(value, field_name):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a date in YYYY-MM-DD format") from exc


def _money(value, places=2):
    quantum = Decimal("1") if places == 0 else Decimal("0.01")
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


def quote_stay(
    room_type,
    arrival_date,
    nights,
    today_date,
    home_game_dates,
    rain_chance,
    currency,
    rate,
):
    """Print and return a Foxglove Inn stay quote."""
    if room_type not in BASE_RATES:
        raise ValueError(f"room_type must be one of: {', '.join(BASE_RATES)}")
    if not isinstance(nights, int) or isinstance(nights, bool) or nights < 1:
        raise ValueError("nights must be a positive integer")
    if not isinstance(currency, str) or len(currency) != 3 or not currency.isalpha():
        raise ValueError("currency must be a three-letter code")
    currency = currency.upper()

    arrival = _parse_date(arrival_date, "arrival_date")
    today = _parse_date(today_date, "today_date")
    game_dates = {_parse_date(value, "home_game_dates entry") for value in home_game_dates}

    if not isinstance(rain_chance, dict):
        raise ValueError("rain_chance must be a dictionary")
    parsed_rain = {}
    for key, chance in rain_chance.items():
        parsed_date = _parse_date(key, "rain_chance date")
        if not isinstance(chance, (int, float, Decimal)) or isinstance(chance, bool) or not 0 <= chance <= 100:
            raise ValueError("rain_chance values must be percentages from 0 to 100")
        parsed_rain[parsed_date] = Decimal(str(chance))

    rate_decimal = Decimal(str(rate))
    if rate_decimal <= 0:
        raise ValueError("rate must be greater than zero")

    # Print every input before printing any quote calculations.
    print(f"room_type: {room_type}")
    print(f"arrival_date: {arrival_date}")
    print(f"nights: {nights}")
    print(f"today_date: {today_date}")
    print(f"home_game_dates: {home_game_dates}")
    print(f"rain_chance: {rain_chance}")
    print(f"currency: {currency}")
    print(f"rate: {rate}")
    print()

    base_rate = BASE_RATES[room_type]
    nightly_quotes = []
    subtotal = Decimal("0")
    forecast_count = 0
    rainy_forecast_count = 0

    for offset in range(nights):
        night = arrival + timedelta(days=offset)
        is_game_night = night in game_dates or (night + timedelta(days=1)) in game_dates
        if is_game_night:
            multiplier = Decimal("1.6")
            rule = "game night (home game date or day before)"
        elif night.weekday() in (4, 5):
            multiplier = Decimal("1.2")
            rule = "Friday/Saturday night"
        else:
            multiplier = Decimal("1")
            rule = "base rate"

        price = base_rate * multiplier
        subtotal += price
        weekday = night.strftime("%A")
        nightly_quotes.append({
            "date": night.isoformat(),
            "weekday": weekday,
            "rule": rule,
            "price_usd": _money(price),
        })
        print(f"{night.isoformat()} ({weekday}): {rule}; ${_money(price):.2f}")

        if night in parsed_rain:
            forecast_count += 1
            if parsed_rain[night] >= 60:
                rainy_forecast_count += 1

    subtotal = _money(subtotal)
    print(f"room subtotal: ${subtotal:.2f}")

    lead_time = (arrival - today).days
    if lead_time <= 7:
        lead_adjustment_percent = Decimal("10")
        lead_adjustment = subtotal * Decimal("0.10")
        lead_description = "10% added (lead time is 7 days or fewer)"
    elif lead_time >= 60:
        lead_adjustment_percent = Decimal("-10")
        lead_adjustment = -subtotal * Decimal("0.10")
        lead_description = "10% taken off (lead time is 60 days or more)"
    else:
        lead_adjustment_percent = Decimal("0")
        lead_adjustment = Decimal("0")
        lead_description = "no adjustment"
    print(f"lead time: {lead_time} days; {lead_description}")

    after_lead = subtotal + lead_adjustment
    if nights >= 3:
        length_adjustment_percent = Decimal("-8")
        length_adjustment = -after_lead * Decimal("0.08")
        length_description = "8% taken off (stay is 3 nights or more)"
    else:
        length_adjustment_percent = Decimal("0")
        length_adjustment = Decimal("0")
        length_description = "no adjustment"
    print(f"length of stay adjustment: {length_description}")

    usd_total = _money(after_lead + length_adjustment)
    converted_total = usd_total * rate_decimal
    currency_places = 0 if currency in WHOLE_CURRENCY_CODES else 2
    converted_total = _money(converted_total, currency_places)
    converted_display = f"{converted_total:.0f}" if currency_places == 0 else f"{converted_total:.2f}"
    print(f"US dollar total: ${usd_total:.2f}")
    print(f"total in {currency}: {converted_display} {currency}")

    if forecast_count < nights / 2:
        package = "no recommendation, the forecast does not reach these dates"
        package_reason = f"forecast covers {forecast_count} of {nights} nights, which is fewer than half"
    elif rainy_forecast_count > forecast_count / 2:
        package = "Rainy Day Package"
        package_reason = f"{rainy_forecast_count} of {forecast_count} forecast nights have rain chance of 60% or more"
    else:
        package = "Trail Package"
        package_reason = f"only {rainy_forecast_count} of {forecast_count} forecast nights have rain chance of 60% or more"
    print(f"package: {package}; reason: {package_reason}")

    return {
        "room_subtotal_usd": subtotal,
        "lead_time_days": lead_time,
        "lead_adjustment_percent": lead_adjustment_percent,
        "length_of_stay_adjustment_percent": length_adjustment_percent,
        "usd_total": usd_total,
        "converted_total": converted_total,
        "currency": currency,
        "package": package,
        "package_reason": package_reason,
        "nightly_quotes": nightly_quotes,
    }


if __name__ == "__main__":
    quote_stay(
        room_type="King Room",
        arrival_date="2026-11-13",
        nights=3,
        today_date="2026-10-22",
        home_game_dates=["2026-11-14"],
        rain_chance={},
        currency="EUR",
        rate=0.89,
    )
