"""
Unit tests for services/esg_auditor.py — satellite-driven carbon-neutral
scoring.

These tests double as regression coverage for the ``reforestation_area``
field-name fix: the typo (``reforestification_area``) made
``_generate_satellite_data`` raise, which ``calculate_carbon_neutral_score``
swallowed into ``{"success": False}`` — every score silently failed.
"""

from datetime import datetime, timedelta, timezone

import pytest

from services.esg_auditor import (
    CarbonNeutralLevel,
    ESGAuditor,
    SatelliteEnvironmentalData,
)


@pytest.fixture
def auditor():
    """Fresh auditor so state never leaks between tests.

    The module-level ``esg_auditor`` singleton is shared with the live
    ``/api/v4/esg/*`` endpoints, so unit tests must use their own instance.
    """
    return ESGAuditor()


def make_satellite_data(**overrides) -> SatelliteEnvironmentalData:
    """Build satellite data with neutral defaults; individual fields overridable."""
    fields = dict(
        listing_id="listing-1",
        location_coordinates={"latitude": 0.0, "longitude": 0.0},
        deforestation_area=0.0,
        reforestation_area=0.0,
        carbon_sequestered=0.0,
        carbon_emitted=0.0,
        water_quality_index=80.0,
        air_quality_index=75.0,
        biodiversity_index=70.0,
        land_use_change=60.0,
        satellite_verification=True,
        last_updated=datetime.now(timezone.utc),
    )
    fields.update(overrides)
    return SatelliteEnvironmentalData(**fields)


class TestSatelliteDataGeneration:
    """_generate_satellite_data — the site of the reforestation_area typo fix."""

    async def test_generates_satellite_record_with_reforestation_area(self, auditor):
        data = await auditor._generate_satellite_data(
            "listing-1", {"latitude": 10.0, "longitude": 20.0}
        )

        assert isinstance(data, SatelliteEnvironmentalData)
        assert data.listing_id == "listing-1"
        assert data.deforestation_area == pytest.approx(1.0)
        assert data.reforestation_area == pytest.approx(3.0)
        assert data.satellite_verification is True
        assert data.last_updated <= datetime.now(timezone.utc)

    async def test_carbon_figures_derived_from_areas(self, auditor):
        data = await auditor._generate_satellite_data(
            "listing-1", {"latitude": 10.0, "longitude": 20.0}
        )

        assert data.carbon_sequestered == pytest.approx(3.0 * 50)  # 50 t/km2
        assert data.carbon_emitted == pytest.approx(1.0 * 100)     # 100 t/km2

    async def test_satellite_data_is_cached_per_listing(self, auditor):
        location = {"latitude": 5.0, "longitude": 6.0}
        first = await auditor._get_satellite_environmental_data("listing-1", location)
        second = await auditor._get_satellite_environmental_data(
            "listing-1", {"latitude": 99.0, "longitude": 99.0}
        )

        # Less than 7 days old -> the cached record wins over the new location.
        assert first is second



class TestCarbonNeutralScore:
    """End-to-end scoring flow (calculate_carbon_neutral_score)."""

    async def test_full_scoring_flow_succeeds(self, auditor):
        result = await auditor.calculate_carbon_neutral_score(
            {
                "listing_id": "listing-1",
                "mineral_type": "gold",
                "location": {"latitude": 9.0, "longitude": 38.0},
            }
        )

        assert result["success"] is True
        score = result["esg_score"]
        for key in (
            "overall_score",
            "environmental_score",
            "social_score",
            "governance_score",
        ):
            assert 0 <= score[key] <= 100, key
        # balance = 285 sequestered - 90 emitted = 195 -> carbon_aware
        assert score["carbon_balance"] == pytest.approx(195.0)
        assert score["carbon_neutral_level"] == "carbon_aware"
        assert score["satellite_verified"] is True

    async def test_satellite_payload_exposes_reforestation_area(self, auditor):
        """Regression: the typo made this whole call return success=False."""
        result = await auditor.calculate_carbon_neutral_score(
            {
                "listing_id": "listing-1",
                "mineral_type": "gold",
                "location": {"latitude": 9.0, "longitude": 38.0},
            }
        )

        assert result["success"] is True
        # 38 * 0.15 = 5.7 km2 of reforestation in the satellite payload
        assert result["satellite_data"]["reforestation_area"] == pytest.approx(5.7)
        assert result["satellite_data"]["deforestation_area"] == pytest.approx(0.9)

    async def test_neutral_location_scores_are_deterministic(self, auditor):
        result = await auditor.calculate_carbon_neutral_score(
            {
                "listing_id": "listing-2",
                "mineral_type": "copper",
                "location": {"latitude": 0.0, "longitude": 0.0},
            }
        )

        assert result["success"] is True
        score = result["esg_score"]
        assert score["environmental_score"] == pytest.approx(63.25)
        assert score["social_score"] == pytest.approx(100.0)   # clamped from 130
        assert score["governance_score"] == pytest.approx(100.0)  # clamped from 130
        assert score["overall_score"] == pytest.approx(85.3)
        assert score["carbon_balance"] == pytest.approx(0.0)
        assert score["carbon_neutral_level"] == "carbon_neutral"

    async def test_result_is_cached_on_the_auditor(self, auditor):
        listing = {
            "listing_id": "listing-3",
            "mineral_type": "gold",
            "location": {"latitude": 1.0, "longitude": 1.0},
        }
        await auditor.calculate_carbon_neutral_score(listing)

        assert "listing-3" in auditor.esg_scores
        assert "listing-3" in auditor.satellite_data

    async def test_missing_required_fields_returns_error_payload(self, auditor):
        result = await auditor.calculate_carbon_neutral_score(
            {"listing_id": "listing-4"}
        )

        assert result["success"] is False


class TestCarbonNeutralLevels:
    """Threshold table for _determine_carbon_neutral_level (inclusive bounds)."""

    @pytest.mark.parametrize(
        ("balance", "expected"),
        [
            (-150.0, CarbonNeutralLevel.CARBON_NEGATIVE),
            (-100.0, CarbonNeutralLevel.CARBON_NEGATIVE),  # boundary is inclusive
            (-0.01, CarbonNeutralLevel.CARBON_NEUTRAL),
            (0.0, CarbonNeutralLevel.CARBON_NEUTRAL),
            (25.0, CarbonNeutralLevel.LOW_CARBON),
            (50.0, CarbonNeutralLevel.LOW_CARBON),
            (51.0, CarbonNeutralLevel.CARBON_AWARE),
            (200.0, CarbonNeutralLevel.CARBON_AWARE),
            (201.0, CarbonNeutralLevel.CARBON_UNTRACKED),
        ],
    )
    async def test_thresholds(self, auditor, balance, expected):
        level = await auditor._determine_carbon_neutral_level(balance)
        assert level == expected


class TestEnvironmentalScore:
    async def test_neutral_defaults(self, auditor):
        score = await auditor._calculate_environmental_score(make_satellite_data())
        assert score == pytest.approx(63.25)

    async def test_reforestation_improves_score(self, auditor):
        baseline = await auditor._calculate_environmental_score(make_satellite_data())
        improved = await auditor._calculate_environmental_score(
            make_satellite_data(reforestation_area=10.0)
        )
        # 10 km2 * 0.3 benefit factor
        assert improved - baseline == pytest.approx(3.0)

    async def test_score_clamped_to_upper_bound(self, auditor):
        score = await auditor._calculate_environmental_score(
            make_satellite_data(reforestation_area=10_000.0)
        )
        assert score == 100.0

    async def test_score_clamped_to_lower_bound(self, auditor):
        score = await auditor._calculate_environmental_score(
            make_satellite_data(
                deforestation_area=10_000.0,
                water_quality_index=0.0,
                air_quality_index=0.0,
                biodiversity_index=0.0,
                land_use_change=0.0,
            )
        )
        assert score == 0.0


class TestSocialAndGovernanceScores:
    async def test_social_score_baseline(self, auditor):
        score = await auditor._calculate_social_score({}, make_satellite_data())
        assert score == 100.0  # clamped from 50 + 50

    async def test_social_score_environmental_adjustments(self, auditor):
        score = await auditor._calculate_social_score(
            {}, make_satellite_data(deforestation_area=10.0, reforestation_area=2.0)
        )
        # 100 - (10 * 5 deforestation penalty) + (2 * 3 reforestation benefit)
        assert score == pytest.approx(56.0)

    async def test_governance_score_clamped(self, auditor):
        score = await auditor._calculate_governance_score({})
        assert score == 100.0  # clamped from 50 + 80



class TestCertificates:
    async def test_unknown_listing(self, auditor):
        result = await auditor.get_esg_certificate("does-not-exist")
        assert result == {"success": False, "error": "ESG score not found"}

    async def test_valid_certificate(self, auditor):
        await auditor.calculate_carbon_neutral_score(
            {
                "listing_id": "listing-cert",
                "mineral_type": "gold",
                "location": {"latitude": 9.0, "longitude": 38.0},
            }
        )

        result = await auditor.get_esg_certificate("listing-cert")

        assert result["success"] is True
        cert = result["certificate"]
        assert cert["listing_id"] == "listing-cert"
        assert cert["carbon_neutral_level"] == "carbon_aware"
        assert cert["satellite_verified"] is True
        assert cert["verification_method"] == "Satellite Data Analysis"
        assert cert["audit_trail"]
        assert "Paris Agreement" in cert["compliance_standards"]
        assert datetime.fromisoformat(cert["valid_until"]) > datetime.now(timezone.utc)

    async def test_expired_certificate(self, auditor):
        await auditor.calculate_carbon_neutral_score(
            {
                "listing_id": "listing-expired",
                "mineral_type": "gold",
                "location": {"latitude": 9.0, "longitude": 38.0},
            }
        )
        auditor.esg_scores["listing-expired"].valid_until = (
            datetime.now(timezone.utc) - timedelta(seconds=1)
        )

        result = await auditor.get_esg_certificate("listing-expired")
        assert result == {"success": False, "error": "ESG certificate expired"}


class TestScoreUpdates:
    async def test_update_requires_existing_score(self, auditor):
        result = await auditor.update_esg_score("unknown", {"location": {}})
        assert result == {"success": False, "error": "ESG score not found"}

    async def test_update_recalculates_and_records_previous_scores(self, auditor):
        await auditor.calculate_carbon_neutral_score(
            {
                "listing_id": "listing-upd",
                "mineral_type": "gold",
                "location": {"latitude": 0.0, "longitude": 0.0},
            }
        )
        original = auditor.esg_scores["listing-upd"].overall_score
        assert original == pytest.approx(85.3)

        # Drop the cache so the refresh uses the new location's satellite pass.
        auditor.satellite_data.clear()

        result = await auditor.update_esg_score(
            "listing-upd", {"location": {"latitude": 30.0, "longitude": 0.0}}
        )

        assert result["success"] is True
        updated = result["updated_scores"]
        # 30 -> 3 km2 deforestation, 0 reforestation: worse environment,
        # carbon balance -300 t -> carbon_negative (net removal).
        assert updated["overall_score"] == pytest.approx(73.84)
        assert updated["carbon_neutral_level"] == "carbon_negative"
        assert updated["overall_score"] != original

        audit_entry = auditor.esg_scores["listing-upd"].audit_trail[-1]
        assert audit_entry["action"] == "esg_score_update"
        # Regression: previous_scores must hold the PRE-update value, not the
        # newly written one.
        assert audit_entry["previous_scores"]["overall"] == pytest.approx(85.3)
        assert audit_entry["updated_scores"]["overall"] == pytest.approx(73.84)



class TestSummary:
    async def test_empty_summary(self, auditor):
        result = await auditor.get_esg_summary()

        assert result["success"] is True
        assert result["total_listings"] == 0
        assert result["average_scores"] == {}
        assert result["satellite_verified"] == 0

    async def test_summary_after_scoring(self, auditor):
        for idx, (lat, lon) in enumerate([(0.0, 0.0), (9.0, 38.0)]):
            result = await auditor.calculate_carbon_neutral_score(
                {
                    "listing_id": f"summary-{idx}",
                    "mineral_type": "gold",
                    "location": {"latitude": lat, "longitude": lon},
                }
            )
            assert result["success"] is True

        summary = await auditor.get_esg_summary()

        assert summary["success"] is True
        assert summary["total_listings"] == 2
        assert summary["satellite_verified"] == 2
        assert summary["satellite_verified_percentage"] == 100.0
        assert set(summary["carbon_neutral_distribution"]) == {
            "carbon_neutral",
            "carbon_aware",
        }
        assert 0 <= summary["average_scores"]["overall"] <= 100


class TestESGEndpoints:
    """HTTP round-trips through the shared esg_auditor singleton in app.py."""

    def test_calculate_carbon_neutral_score_endpoint(self, client):
        response = client.post(
            "/api/v4/esg/calculate-carbon-neutral-score",
            json={
                "listing_data": {
                    "listing_id": "endpoint-listing",
                    "mineral_type": "gold",
                    "location": {"latitude": 9.0, "longitude": 38.0},
                }
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["esg_score"]["carbon_neutral_level"] == "carbon_aware"

    def test_certificate_endpoint_roundtrip(self, client):
        scoring = client.post(
            "/api/v4/esg/calculate-carbon-neutral-score",
            json={
                "listing_data": {
                    "listing_id": "endpoint-cert",
                    "mineral_type": "gold",
                    "location": {"latitude": 9.0, "longitude": 38.0},
                }
            },
        )
        assert scoring.status_code == 200

        response = client.get("/api/v4/esg/certificate/endpoint-cert")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["certificate"]["listing_id"] == "endpoint-cert"

    def test_summary_endpoint(self, client):
        response = client.get("/api/v4/esg/summary")

        assert response.status_code == 200
        assert response.json()["success"] is True

