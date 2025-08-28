#!/usr/bin/env bash
set -euo pipefail
mkdir -p test_documents
cd test_documents

# AWS Well-Architected Framework
if [ ! -f aws_well_architected_framework.pdf ]; then
  curl -L -o aws_well_architected_framework.pdf "https://d1.awsstatic.com/whitepapers/architecture/AWS_Well-Architected_Framework.pdf"
fi

# NIST SP 800-53 Rev. 5
if [ ! -f nist_sp_800_53r5.pdf ]; then
  curl -L -o nist_sp_800_53r5.pdf "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf"
fi

# FAQ
cat > faq.txt <<FAQ
Q: What is a staging environment?
A: A staging environment mirrors production for final testing before release.

Q: What is a rollback?
A: Reverting a deployment to a previous stable version.

Q: What is blue-green deployment?
A: Running two environments (blue and green) to enable zero-downtime releases.

Q: What is canary release?
A: Gradually rolling out changes to a subset of users to reduce risk.

Q: What is observability?
A: The ability to understand system state via logs, metrics, traces.
FAQ

echo "Downloaded test documents."
