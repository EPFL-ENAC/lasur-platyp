#!/usr/bin/env python3
"""Seed the database with fake Record rows attached to an existing campaign.

For local dev/testing only. Generates randomized but structurally realistic
`data`/`typo` payloads (modeled on plans/records.csv, a recent production
export) and creates them through RecordService.create(), so seeded rows
behave exactly like real ones (timestamps, response_id_in_campaign
numbering, etc). Includes professional journeys (freq_mod_pro_journeys) and
their recommendations (typo.reco_pro), not just the personal commute.

email_hash is faked from a reusable pool of "participant{n}@example.test"
addresses hashed the same way the collect app does (sha256 of the
trimmed/lowercased email, see collect/src/utils/hash.ts). Reusing the same
pool size across separate seed runs on different campaigns lets the same
fake participant show up in 2+ campaigns, which is what
LongitudinalService.filter_longitudinal requires to include them.

Usage:
    uv run dotenv -f ../.env run python scripts/seed_records.py --campaign-id 1 --count 20
    uv run dotenv -f ../.env run python scripts/seed_records.py --campaign-id 2 --count 20 --participants 10
"""

import argparse
import asyncio
import hashlib
import random
import secrets
import sys

from sqlmodel import select

from api.db import get_session
from api.models.domain import Campaign
from api.models.query import RecordDraft
from api.services.records import RecordService

MODES = ["car", "moto", "pub", "train", "bike", "walking"]
PRO_MODES = ["car", "train", "plane", "boat", "pub"]
SIMPLE_MODES = ["MA", "TP", "MA+TP", "MA+TIM", "TIM+TP", "TIM"]
AGE_CLASSES = ["18-24", "25-44", "45-64", "65+"]
CONSTRAINTS = ["none", "dependent", "heavy", "night", "disabled", "other"]
EQUIPMENTS = ["bike", "ebike", "tpu_unireso", "tpu_leman_pass", "train_demi_tarif",
              "train_abo_gen", "mob_subs", "moto", "car", "ev"]
LEVERS = ["environment", "flexibility", "collective",
          "finance", "company_vehicle", "coaching", "events", "other"]
RECO_OPTIONS = ["tpu", "vae", "elec", "velo",
                "cargo", "inter", "train", "covoit", "marche"]
PT_PASSES = ["unireso", "cff", "leman_pass"]
ACTIONS = ["budget", "wfh", "bike_parking", "shuttle", "carpool_matching"]
PRO_FEATURE_IDS = ["FR_74218", "FRK11", "CH066", "CH024"]


def fake_location(center_lat: float = 46.2, center_lon: float = 6.14, spread: float = 0.08) -> dict:
    return {
        "lat": round(center_lat + random.uniform(-spread, spread), 6),
        "lon": round(center_lon + random.uniform(-spread, spread), 6),
    }


def fake_hex_id() -> str:
    """A plausible-looking H3-style hex index, e.g. '821f97fffffffff'."""
    resolution = random.choice(["82", "85"])
    return resolution + "".join(random.choices("0123456789abcdef", k=6)) + "fffffff"


def fake_journey() -> dict:
    """A personal commute journey, possibly intermodal (e.g. bike-train-bike)."""
    modes = [random.choice(MODES)]
    if random.random() < 0.3:
        modes = [modes[0], random.choice(MODES), modes[0]]
    elif random.random() < 0.3:
        modes.append(random.choice(MODES))
    journey = {"days": random.randint(1, 5), "modes": modes}
    if random.random() < 0.3:
        journey["days_per"] = random.choice(["week", "month", "year"])
    return journey


def fake_pro_journey() -> dict:
    """A professional (business travel) journey, e.g. to a client site."""
    return {
        "days": random.randint(1, 15),
        "days_per": random.choice(["week", "month", "year"]),
        "hex_id": fake_hex_id(),
        "mode": random.choice(PRO_MODES),
        "location": {
            "feature_id": random.choice(PRO_FEATURE_IDS),
            "level": random.choice(["local", "regional"]),
            **fake_location(),
        },
    }


def fake_change() -> dict:
    """One entry in the 'intention to change commute habits' list."""
    change = {
        "levers": random.sample(LEVERS, k=random.randint(1, 3)),
        "motivation": random.randint(1, 5),
    }
    if "other" in change["levers"] and random.random() < 0.5:
        change["other_levers"] = "flexible schedule"
    return change


def fake_data(workplace: dict) -> dict:
    pro_journeys = [
        fake_pro_journey()
        for _ in range(random.choices([0, 1, 2], weights=[60, 35, 5])[0])
    ]
    changes = [fake_change() for _ in range(random.choices(
        [0, 1, 2], weights=[40, 40, 20])[0])]
    constraint = "none" if random.random() < 0.7 else random.choice(CONSTRAINTS)

    return {
        "version": "3.0.0",
        "origin": {**fake_location(), "address": "Fake street, Geneva"},
        "workplace": workplace,
        "age_class": random.choice(AGE_CLASSES),
        "employment_rate": random.choice([50, 80, 90, 100]),
        "remote_work_rate": random.choice([0, 20, 40, 60]),
        "travel_time": random.randint(5, 60),
        "travel_pro": random.choice([True, False]),
        **{f"needs_{m}": random.choice([0, 1]) for m in MODES},
        **{f"importance_{k}": random.randint(1, 5) for k in [
            "time", "cost", "flex", "comfort", "rel", "most", "env"]},
        "freq_mod_journeys": [fake_journey() for _ in range(random.randint(1, 3))],
        "freq_mod_pro_journeys": pro_journeys,
        "changes": changes,
        "constraints": [constraint],
        "equipments": random.sample(EQUIPMENTS, k=random.randint(0, 3)),
        "company_vehicle": random.choice([True, False]),
        "confidentiality": True,
        "terms_conditions": True,
    }


def fake_email_hash(participant_index: int) -> str:
    email = f"participant{participant_index}@example.test"
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()


def fake_reco() -> dict:
    primary = random.choice(RECO_OPTIONS)
    secondary = primary if random.random() < 0.6 else random.choice(RECO_OPTIONS)
    t_tim = random.randint(4, 30)
    return {
        "pt_pass": random.choice(PT_PASSES),
        "reco_inter": [primary, secondary],
        "reco_simple": [random.choice(SIMPLE_MODES) for _ in range(2)],
        "simple_labels": [random.choice(SIMPLE_MODES) for _ in range(2)],
        "complex_labels": [random.choice(MODES), random.choice(MODES)],
        "bravo": [0] if random.random() < 0.7 else [0, random.randint(1, 2)],
        "t_traj_mm": {
            "oid": random.randint(1000, 3000),
            "did": 281,
            "t_tim": t_tim,
            "t_tp": t_tim + random.randint(0, 20),
            "t_velo": t_tim + random.randint(0, 20),
        },
    }


def fake_reco_pro() -> dict:
    return {"reco_pros": [random.choice(PRO_MODES)]}


def fake_reco_actions() -> dict:
    actions = {"mesures_globa": random.sample(ACTIONS, k=2) +
               [random.choice(["global1", "global2"])]}
    if random.random() < 0.5:
        actions["mesure_dt1"] = "tpg_pass"
        actions["mesure_dt2"] = "tpg_pass"
    return actions


def fake_typo() -> dict:
    return {
        "reco": fake_reco(),
        "reco_pro": fake_reco_pro(),
        "reco_actions": fake_reco_actions(),
    }


async def seed(campaign_id: int, count: int, participants: int, email_hash_rate: float) -> None:
    async for session in get_session():
        campaign = (await session.exec(
            select(Campaign).where(Campaign.id == campaign_id)
        )).one_or_none()
        if campaign is None:
            print(f"Campaign {campaign_id} not found", file=sys.stderr)
            sys.exit(1)

        workplace = fake_location()
        workplace["address"] = campaign.name
        workplace["name"] = campaign.name

        service = RecordService(session)
        for i in range(count):
            email_hash = None
            if random.random() < email_hash_rate:
                email_hash = fake_email_hash(i % participants)
            draft = RecordDraft(
                token=secrets.token_urlsafe(16),
                data=fake_data(workplace),
                typo=fake_typo(),
                email_hash=email_hash,
            )
            record = await service.create(draft, campaign)
            print(
                f"[{i + 1}/{count}] created record id={record.id} token={record.token} "
                f"email_hash={record.email_hash}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-id", type=int, required=True,
                         help="Existing campaign id to attach seeded records to")
    parser.add_argument("--count", type=int, default=10,
                         help="Number of fake records to create (default: 10)")
    parser.add_argument("--participants", type=int, default=None,
                         help="Size of the fake participant pool reused for email_hash "
                         "(default: half of --count, min 1). Use the same value across "
                         "campaigns to simulate returning participants for longitudinal analysis")
    parser.add_argument("--email-hash-rate", type=float, default=0.8,
                         help="Fraction of records that get a fake email_hash; "
                         "the rest are left null, like real incomplete submissions (default: 0.8)")
    parser.add_argument("--random-seed", type=int, default=None,
                         help="Seed the RNG for reproducible output")
    args = parser.parse_args()

    if args.random_seed is not None:
        random.seed(args.random_seed)

    participants = args.participants if args.participants is not None else max(
        1, args.count // 2)

    asyncio.run(seed(args.campaign_id, args.count,
                participants, args.email_hash_rate))


if __name__ == "__main__":
    main()
