# Pre-Commit Validation Issues

## comm_syntax_direct_msg (LOW)
**Issue**: Communication syntax may not be canonical: {{@mesh ::: message}}
**Suggested Fix**: Verify message format follows {{@agent.Name ::: message}} syntax

## staff_name_validation_XO (MEDIUM)  
**Issue**: Non-canonical name for XO
**Suggested Fix**: Replace with canonical name: Maya Shepard

## api_endpoint_unknown_starling (MEDIUM)
**Issue**: Unknown API endpoint: /api/relay/starling
**Suggested Fix**: Verify endpoint is required or use canonical relay endpoints

## api_endpoint_unknown_riverthread (MEDIUM)
**Issue**: Unknown API endpoint: /api/relay/riverthread
**Suggested Fix**: Verify endpoint is required or use canonical relay endpoints

## comm_syntax_direct_msg (LOW)
**Issue**: Communication syntax may not be canonical: {{@mesh ::: Arbitration required}}
**Suggested Fix**: Verify message format follows {{@agent.Name ::: message}} syntax

## comm_syntax_direct_msg (LOW)
**Issue**: Communication syntax may not be canonical: {{@ethics ::: Protocol violation detected}}
**Suggested Fix**: Verify message format follows {{@agent.Name ::: message}} syntax

## comm_syntax_direct_msg (LOW)
**Issue**: Communication syntax may not be canonical: {{@mesh ::: Drift event detected}}
**Suggested Fix**: Verify message format follows {{@agent.Name ::: message}} syntax

---

**Note**: This file contains validation issues found during pre-commit checks.
All encoded/encrypted content has been cleaned for canonical compliance.

**Canonical Standards**:
- XO: Maya Shepard  
- anchor_seed: EOS_SEED_ORION
- ethics_protocol: Picard_Delta_3
- Communication format: {{@agent.Name ::: message}}
