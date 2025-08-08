"""Seed database with initial data."""

import asyncio
from datetime import datetime, timedelta
from sqlmodel import Session
from passlib.context import CryptContext

from api.utils.database import engine
from api.models import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_initial_data():
    """Create initial seed data."""
    with Session(engine) as session:
        # Create default roles
        admin_role = Role(
            name="admin",
            description="Administrator role with full permissions",
            permissions={
                "users": ["create", "read", "update", "delete"],
                "agents": ["create", "read", "update", "delete"],
                "calls": ["read", "export"],
                "settings": ["read", "update"],
            },
            is_system=True
        )
        
        user_role = Role(
            name="user",
            description="Standard user role",
            permissions={
                "agents": ["read", "update"],
                "calls": ["read"],
                "settings": ["read"],
            },
            is_system=True
        )
        
        session.add(admin_role)
        session.add(user_role)
        session.commit()
        
        # Create demo organization
        demo_org = Organization(
            name="Demo Restaurant GmbH",
            slug="demo-restaurant",
            description="Demo Restaurant für VocalIQ Tests",
            email="info@demo-restaurant.de",
            phone="+49 30 12345678",
            business_type="restaurant",
            business_hours={
                "monday": {"open": "11:00", "close": "22:00"},
                "tuesday": {"open": "11:00", "close": "22:00"},
                "wednesday": {"open": "11:00", "close": "22:00"},
                "thursday": {"open": "11:00", "close": "22:00"},
                "friday": {"open": "11:00", "close": "23:00"},
                "saturday": {"open": "12:00", "close": "23:00"},
                "sunday": {"open": "12:00", "close": "21:00"},
            },
            subscription_plan="professional",
            max_agents=5,
            max_calls_per_month=1000,
            max_minutes_per_month=5000,
        )
        
        session.add(demo_org)
        session.commit()
        
        # Create demo user
        demo_user = User(
            email="demo@vocaliq.ai",
            full_name="Demo User",
            hashed_password=pwd_context.hash("demo123"),
            is_active=True,
            is_verified=True,
            verified_at=datetime.utcnow(),
            organization_id=demo_org.id,
            role_id=admin_role.id,
            language="de",
            timezone="Europe/Berlin",
        )
        
        session.add(demo_user)
        session.commit()
        
        # Create demo agent
        demo_agent = Agent(
            name="Restaurant Assistent",
            description="KI-Assistent für Reservierungen und Bestellungen",
            organization_id=demo_org.id,
            greeting_message="Guten Tag, vielen Dank für Ihren Anruf beim Demo Restaurant. Mein Name ist Anna, wie kann ich Ihnen helfen?",
            voice_id="de-DE-Neural2-F",
            system_prompt="""Du bist Anna, die freundliche KI-Assistentin des Demo Restaurants. 
            Deine Aufgaben:
            - Tischreservierungen entgegennehmen
            - Öffnungszeiten mitteilen
            - Fragen zur Speisekarte beantworten
            - Bestellungen für Abholung aufnehmen
            
            Sei immer höflich, professionell und hilfsbereit. Frage nach allen notwendigen Informationen für Reservierungen (Datum, Uhrzeit, Personenzahl, Name, Telefonnummer).""",
            personality_traits=["freundlich", "professionell", "hilfsbereit", "geduldig"],
            capabilities={
                "reservations": True,
                "orders": True,
                "information": True,
                "calendar_booking": True,
            },
            knowledge_base_enabled=True,
        )
        
        session.add(demo_agent)
        session.commit()
        
        # Create knowledge base entries
        kb_entries = [
            AgentKnowledgeBase(
                title="Öffnungszeiten",
                content="Montag bis Donnerstag: 11:00 - 22:00 Uhr, Freitag und Samstag: 11:00 - 23:00 Uhr, Sonntag: 12:00 - 21:00 Uhr",
                category="information",
                tags=["öffnungszeiten", "zeiten", "geöffnet"],
                organization_id=demo_org.id,
            ),
            AgentKnowledgeBase(
                title="Spezialitäten",
                content="Unsere Spezialitäten sind: Wiener Schnitzel, Rinderrouladen, vegetarische Gemüselasagne, und unser berühmter Apfelstrudel.",
                category="menu",
                tags=["speisekarte", "essen", "spezialitäten", "menü"],
                organization_id=demo_org.id,
            ),
            AgentKnowledgeBase(
                title="Reservierungspolitik",
                content="Reservierungen können bis zu 4 Wochen im Voraus gemacht werden. Für Gruppen über 8 Personen bitten wir um telefonische Rücksprache. Stornierungen sind bis 2 Stunden vor der Reservierung möglich.",
                category="policy",
                tags=["reservierung", "stornierung", "gruppe"],
                organization_id=demo_org.id,
            ),
        ]
        
        for kb in kb_entries:
            session.add(kb)
        
        session.commit()
        
        print("✅ Database seeded successfully!")
        print(f"Demo login: demo@vocaliq.ai / demo123")


if __name__ == "__main__":
    create_initial_data()