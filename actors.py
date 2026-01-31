from state_actor import StateActorAgent

china_agent = StateActorAgent(
    name="China",
    identity={
        "regime_type": "authoritarian",
        "historical_narrative": "Century of humiliation followed by resurgence",
        "self_image": "Rising great power seeking rightful place",
        "core_values": ["sovereignty", "non-interference", "multipolarity"],
        "regional_role": "Regional hegemon in Asia-Pacific"
    },
    relationships={
        "USA": -0.3,      # Rivalry
        "Russia": 0.6,    # Strategic partnership
        "ASEAN": 0.2,     # Mixed
        "EU": 0.1         # Economic ties, political tension
    },
    norms_internalized=[
        "territorial_sovereignty",
        "economic_interdependence",
        "UN_Charter_principles"
    ],
    norms_contested=[
        "liberal_intervention",
        "universal_human_rights",
        "freedom_of_navigation_US_interpretation"
    ]
)

# Create USA agent
usa_agent = StateActorAgent(
    name="United_States",
    identity={
        "regime_type": "democratic",
        "historical_narrative": "Leader of free world, defender of liberal order",
        "self_image": "Indispensable nation, global security provider",
        "core_values": ["democracy", "human_rights", "rule_of_law", "free_markets"],
        "regional_role": "Global hegemon with worldwide commitments"
    },
    relationships={
        "China": -0.3,
        "Russia": -0.6,
        "Japan": 0.7,
        "South_Korea": 0.7
    },
    norms_internalized=[
        "liberal_intervention",
        "freedom_of_navigation",
        "alliance_commitments",
        "nuclear_non_proliferation"
    ],
    norms_contested=[
        "ICC_jurisdiction",
        "absolute_sovereignty"
    ]
)

# Create Russia agent
russia_agent = StateActorAgent(
    name="Russia",
    identity={
        "regime_type": "authoritarian",
        "historical_narrative": "Former superpower in multipolarity, civilizational leader",
        "self_image": "Defender of traditional values, great power resisting Western hegemony",
        "core_values": ["sovereignty", "sphere_of_influence", "civilizational_identity", "multipolarity"],
        "regional_role": "Regional hegemon in Eurasia, nuclear power"
    },
    relationships={
        "USA": -0.7,      # Strategic rivalry
        "China": 0.6,     # Strategic partnership
        "Europe": -0.4,   # Contested sphere
        "Ukraine": -0.8   # Contested influence
    },
    norms_internalized=[
        "territorial_sovereignty",
        "spheres_of_influence",
        "nuclear_deterrence",
        "great_power_politics"
    ],
    norms_contested=[
        "liberal_intervention",
        "NATO_expansion",
        "color_revolutions",
        "Western_values_universalism"
    ]
)


async def main():
    """Test the China agent by displaying its identity and configuration."""
    
    print("=" * 60)
    print("Testing China Agent")
    print("=" * 60)
    print(f"\nAgent Name: {china_agent.name}")
    print(f"\nNational Identity:")
    for key, value in china_agent.national_identity.items():
        print(f"  {key}: {value}")
    
    print(f"\nRelationships:")
    for country, trust_level in china_agent.relationships.items():
        print(f"  {country}: {trust_level}")
    
    print(f"\nInternalized Norms:")
    for norm in china_agent.norms_internalized:
        print(f"  - {norm}")
    
    print(f"\nContested Norms:")
    for norm in china_agent.norms_contested:
        print(f"  - {norm}")
    
    print("\n" + "=" * 60)
    print("China Agent successfully instantiated with constructivist identity!")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())