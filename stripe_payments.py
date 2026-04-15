"""
stripe_payments.py — Gochara Karmique
Gestion des paiements Stripe : abonnement 1,99€ + one-shots 4,99€ / 19,99€
"""

import os
import stripe

# ── Price IDs ────────────────────────────────────────────────────────────────
PRICE_SUB       = os.environ.get("KARMIC_STRIPE_PRICE_SUB",      "price_1TMNG4I25M0U9qA3ViFPGrJ7")  # 1,99€/mois
PRICE_ESSENTIAL = os.environ.get("KARMIC_STRIPE_PRICE_ESSENTIAL", "price_1TMNI2I25M0U9qA3TGkmiPtZ")  # 4,99€
PRICE_COMPLETE  = os.environ.get("KARMIC_STRIPE_PRICE_COMPLETE",  "price_1TMNKYI25M0U9qA31GzAjHR0")  # 19,99€

# Plans → nombre de synthèses accordées
PLAN_SYNTHESES = {
    "sub":       1,   # abonnement mensuel → 1 synthèse/mois
    "essential": 1,   # one-shot → 1 synthèse
    "complete":  1,   # one-shot → 1 synthèse complète
    "free":      0,
}

PLAN_LABELS = {
    "sub":       "Abonnement Alertes",
    "essential": "Synthèse Essentielle",
    "complete":  "Lecture Complète",
    "free":      "Gratuit",
}


def _stripe_client():
    stripe.api_key = os.environ.get("KARMIC_STRIPE_SECRET_KEY", "")
    return stripe


def create_checkout_session(plan: str, user_email: str, pseudo: str, base_url: str) -> str:
    """
    Crée une session Stripe Checkout et retourne l'URL de paiement.

    plan      : "sub" | "essential" | "complete"
    base_url  : ex "https://karmicgochara.app"
    Retourne  : URL Stripe Checkout
    """
    s = _stripe_client()

    price_map = {
        "sub":       PRICE_SUB,
        "essential": PRICE_ESSENTIAL,
        "complete":  PRICE_COMPLETE,
    }
    price_id = price_map.get(plan)
    if not price_id:
        raise ValueError(f"Plan inconnu : {plan}")

    mode = "subscription" if plan == "sub" else "payment"

    session = s.checkout.Session.create(
        customer_email=user_email,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode=mode,
        success_url=f"{base_url}/stripe/success?session_id={{CHECKOUT_SESSION_ID}}&plan={plan}&pseudo={pseudo}",
        cancel_url=f"{base_url}/?payment=cancelled",
        metadata={"pseudo": pseudo, "plan": plan},
    )
    return session.url


def verify_webhook(payload: bytes, sig_header: str) -> dict:
    """
    Vérifie la signature du webhook Stripe et retourne l'événement.
    Lève stripe.error.SignatureVerificationError si invalide.
    """
    s = _stripe_client()
    secret = os.environ.get("KARMIC_STRIPE_WEBHOOK_SECRET", "")
    event = s.Webhook.construct_event(payload, sig_header, secret)
    return event


def get_plan_from_price(price_id: str) -> str:
    """Retourne le plan correspondant à un Price ID."""
    mapping = {
        PRICE_SUB:       "sub",
        PRICE_ESSENTIAL: "essential",
        PRICE_COMPLETE:  "complete",
    }
    return mapping.get(price_id, "free")
