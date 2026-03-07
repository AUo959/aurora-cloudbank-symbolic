# Command Grammar

Use these mappings when translating user intent into mesh CLI calls.

- `@mesh status`
  - `python3 scripts/mesh_router.py status`
- `@mesh Alex Thorne Need a routing decision`
  - `python3 scripts/mesh_router.py send --to alex_thorne --channel private:captain:alex --message "Need a routing decision"`
- `@mesh #crew_lounge Stand up in ten`
  - `python3 scripts/mesh_router.py broadcast --channel "#crew_lounge" --message "Stand up in ten"`
- `@mesh history private:captain:alex`
  - `python3 scripts/mesh_router.py history private:captain:alex`
- `@mesh activate Alex Thorne`
  - `python3 scripts/mesh_router.py activate alex_thorne`
- `@mesh tail`
  - `python3 scripts/mesh_router.py tail --follow`
