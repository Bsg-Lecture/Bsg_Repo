# Ethical Use Guidelines

## ⚠️ IMPORTANT NOTICE

This framework is designed **exclusively for research and educational purposes** to advance the security of electric vehicle charging infrastructure. Misuse of this tool can cause harm to individuals, organizations, and critical infrastructure.

**By using this framework, you agree to:**
1. Use it only for legitimate research and educational purposes
2. Obtain proper authorization before testing any systems
3. Follow responsible disclosure practices
4. Comply with all applicable laws and regulations
5. Never cause harm to real infrastructure or users

---

## Table of Contents

1. [Purpose and Scope](#purpose-and-scope)
2. [Acceptable Use](#acceptable-use)
3. [Prohibited Use](#prohibited-use)
4. [Legal Compliance](#legal-compliance)
5. [Responsible Disclosure](#responsible-disclosure)
6. [Research Ethics](#research-ethics)
7. [Academic Integrity](#academic-integrity)
8. [Institutional Review](#institutional-review)
9. [Reporting Violations](#reporting-violations)
10. [Acknowledgment](#acknowledgment)

---

## Purpose and Scope

### Research Objectives

This framework is designed to:
- **Identify vulnerabilities** in OCPP-based charging infrastructure
- **Quantify security risks** related to charging profile manipulation
- **Develop defense mechanisms** against battery degradation attacks
- **Educate researchers** about EV charging security
- **Advance the field** of cyber-physical security

### Intended Users

- Academic researchers in cybersecurity
- Security professionals conducting authorized assessments
- Students learning about EV charging security
- Industry professionals developing defense mechanisms
- Standards bodies evaluating OCPP security

### Out of Scope

This framework is **NOT** intended for:
- Unauthorized testing of production systems
- Malicious attacks on real infrastructure
- Commercial exploitation without proper licensing
- Causing harm to individuals or organizations
- Violating laws or regulations

---

## Acceptable Use

### ✅ Permitted Activities

#### 1. Controlled Research Environments

**Allowed:**
- Testing in isolated laboratory networks
- Simulations with no connection to real infrastructure
- Authorized penetration testing with written permission
- Educational demonstrations in classroom settings
- Development of defense mechanisms

**Requirements:**
- Complete isolation from production networks
- No connection to real charging stations or vehicles
- Proper network segmentation and firewalls
- Documented authorization from system owners

**Example:**
```
✅ Running simulation on isolated test network
✅ Using EmuOCPP emulator in lab environment
✅ Testing with permission from charging station manufacturer
```

#### 2. Academic Research

**Allowed:**
- Publishing research findings in peer-reviewed venues
- Presenting results at academic conferences
- Sharing anonymized data with research community
- Collaborating with industry on security improvements

**Requirements:**
- Institutional Review Board (IRB) approval if required
- Ethical review of research methodology
- Responsible disclosure of vulnerabilities
- Protection of sensitive information

**Example:**
```
✅ Publishing paper on OCPP security vulnerabilities
✅ Presenting findings at IEEE conference
✅ Sharing simulation data with other researchers
```

#### 3. Security Assessment

**Allowed:**
- Authorized penetration testing
- Security audits with written contracts
- Vulnerability assessments for clients
- Red team exercises with proper authorization

**Requirements:**
- Written authorization from system owner
- Clearly defined scope and boundaries
- Professional liability insurance
- Non-disclosure agreements as appropriate
- Documented rules of engagement

**Example:**
```
✅ Penetration test authorized by charging network operator
✅ Security audit contracted by EV manufacturer
✅ Red team exercise for utility company
```

#### 4. Education and Training

**Allowed:**
- Teaching cybersecurity courses
- Training security professionals
- Demonstrating attack techniques in controlled settings
- Developing educational materials

**Requirements:**
- Institutional approval for curriculum
- Proper supervision of students
- Isolated training environments
- Clear ethical guidelines for students

**Example:**
```
✅ University course on EV charging security
✅ Professional training workshop
✅ Cybersecurity competition in isolated environment
```

---

## Prohibited Use

### ❌ Forbidden Activities

#### 1. Unauthorized Access

**Prohibited:**
- Testing production systems without authorization
- Accessing charging stations without permission
- Intercepting real OCPP communications
- Manipulating real charging profiles

**Consequences:**
- Criminal prosecution under computer fraud laws
- Civil liability for damages
- Academic sanctions
- Professional license revocation

**Example:**
```
❌ Testing attack on public charging station
❌ Intercepting OCPP traffic without authorization
❌ Manipulating real EV charging sessions
```

#### 2. Causing Harm

**Prohibited:**
- Damaging EV batteries
- Disrupting charging services
- Causing financial harm to users or operators
- Creating safety hazards

**Consequences:**
- Criminal charges for property damage
- Civil liability for damages
- Regulatory penalties
- Reputational harm

**Example:**
```
❌ Degrading real EV batteries
❌ Disrupting public charging infrastructure
❌ Causing safety incidents
```

#### 3. Malicious Intent

**Prohibited:**
- Using framework for personal gain through harm
- Extortion or blackmail
- Competitive sabotage
- Terrorism or critical infrastructure attacks

**Consequences:**
- Severe criminal penalties
- Federal prosecution
- International law enforcement action
- Lifetime bans from research community

**Example:**
```
❌ Extorting charging network operators
❌ Sabotaging competitor's infrastructure
❌ Attacking critical infrastructure
```

#### 4. Irresponsible Disclosure

**Prohibited:**
- Publishing vulnerabilities without vendor notification
- Selling exploits to malicious actors
- Sharing attack tools with unauthorized parties
- Disclosing vulnerabilities before patches available

**Consequences:**
- Harm to users and infrastructure
- Legal liability
- Loss of research privileges
- Damage to professional reputation

**Example:**
```
❌ Publishing zero-day exploit without vendor notification
❌ Selling attack tools on dark web
❌ Sharing vulnerabilities publicly before patches
```

---

## Legal Compliance

### Applicable Laws

Users must comply with all applicable laws, including but not limited to:

#### United States

- **Computer Fraud and Abuse Act (CFAA)** - 18 U.S.C. § 1030
- **Electronic Communications Privacy Act (ECPA)** - 18 U.S.C. § 2510
- **Digital Millennium Copyright Act (DMCA)** - 17 U.S.C. § 1201
- **State computer crime laws**

#### European Union

- **General Data Protection Regulation (GDPR)**
- **Network and Information Security (NIS) Directive**
- **Cybersecurity Act**
- **National computer crime laws**

#### International

- **Budapest Convention on Cybercrime**
- **National cybersecurity laws**
- **Critical infrastructure protection regulations**

### Authorization Requirements

#### Written Permission

Obtain written authorization before testing:
- Charging station operators
- Charging network providers
- EV manufacturers
- Utility companies
- Property owners

#### Scope Definition

Clearly define:
- Systems to be tested
- Testing methods and tools
- Time windows for testing
- Acceptable impact levels
- Reporting procedures

#### Documentation

Maintain records of:
- Authorization letters
- Scope agreements
- Test plans
- Results and findings
- Communications with stakeholders

---

## Responsible Disclosure

### Vulnerability Disclosure Process

#### Step 1: Discovery

When you discover a vulnerability:
1. **Stop testing** immediately after confirmation
2. **Document** the vulnerability thoroughly
3. **Assess** potential impact and severity
4. **Do not** exploit further or share publicly

#### Step 2: Vendor Notification

Contact the affected vendor:
1. **Identify** appropriate security contact
2. **Send** detailed vulnerability report
3. **Provide** proof of concept (if safe)
4. **Offer** to assist with remediation

**Contact Methods:**
- Vendor security email (security@vendor.com)
- Bug bounty programs
- CERT/CC or national CERT
- Industry ISACs (Information Sharing and Analysis Centers)

#### Step 3: Coordination

Work with vendor to:
1. **Verify** the vulnerability
2. **Assess** impact and severity
3. **Develop** patches or mitigations
4. **Test** proposed fixes
5. **Coordinate** disclosure timeline

**Recommended Timeline:**
- Initial response: 7 days
- Patch development: 30-90 days
- Public disclosure: After patch availability

#### Step 4: Public Disclosure

After patch is available:
1. **Coordinate** disclosure date with vendor
2. **Prepare** advisory with technical details
3. **Credit** researchers appropriately
4. **Publish** findings responsibly

**Disclosure Channels:**
- Academic publications
- Security conferences
- Vendor security advisories
- CVE database
- Research blogs

### Disclosure Template

```
Subject: Security Vulnerability in [Product/System]

Dear [Vendor] Security Team,

I am a security researcher at [Institution] and have discovered a 
vulnerability in [Product/System] that could allow [Impact].

Vulnerability Details:
- Product: [Name and version]
- Vulnerability Type: [e.g., Charging profile manipulation]
- Severity: [Critical/High/Medium/Low]
- Impact: [Description of potential harm]

I am committed to responsible disclosure and would like to work with 
you to address this issue. I can provide additional technical details 
and proof of concept upon request.

Please acknowledge receipt of this report and let me know your 
preferred process for coordination.

Best regards,
[Your Name]
[Contact Information]
```

---

## Research Ethics

### Ethical Principles

#### 1. Beneficence

**Do good:**
- Advance security of EV charging infrastructure
- Protect users from harm
- Contribute to public safety
- Share knowledge with community

#### 2. Non-Maleficence

**Do no harm:**
- Avoid damaging systems or data
- Minimize disruption to services
- Protect user privacy
- Consider unintended consequences

#### 3. Autonomy

**Respect rights:**
- Obtain informed consent when required
- Respect system owner decisions
- Honor confidentiality agreements
- Protect intellectual property

#### 4. Justice

**Be fair:**
- Share benefits of research broadly
- Avoid exploiting vulnerabilities for personal gain
- Consider impact on vulnerable populations
- Promote equitable access to security

### Ethical Review

#### When IRB Review is Required

Seek Institutional Review Board approval when research involves:
- Human subjects (e.g., user studies)
- Personal data collection
- Potential harm to individuals
- Vulnerable populations

#### Ethics Checklist

Before starting research, consider:
- [ ] Have I obtained necessary authorizations?
- [ ] Could my research cause harm?
- [ ] Am I protecting privacy and confidentiality?
- [ ] Have I considered unintended consequences?
- [ ] Am I following responsible disclosure practices?
- [ ] Do I have appropriate insurance and liability protection?
- [ ] Have I consulted with ethics experts?

---

## Academic Integrity

### Citation and Attribution

#### Citing This Framework

If you use this framework in your research:

```bibtex
@software{emuocpp_attack_simulation,
  title={Charging Profile Poisoning Attack Simulation Framework},
  author={[Authors]},
  year={2024},
  url={https://github.com/vfg27/EmuOCPP},
  note={Research framework for OCPP security analysis}
}
```

#### Acknowledging Contributors

- Credit original authors
- Acknowledge funding sources
- Recognize collaborators
- Cite related work appropriately

### Data Sharing

#### Open Science Principles

- Share code and data when possible
- Use open-source licenses
- Publish in open-access venues
- Make results reproducible

#### Protecting Sensitive Information

Do not share:
- Exploits before patches available
- Personally identifiable information
- Proprietary system details
- Confidential business information

---

## Institutional Review

### University Policies

Researchers at academic institutions must:
- Follow institutional research policies
- Obtain IRB approval when required
- Comply with export control regulations
- Respect intellectual property policies
- Maintain research integrity

### Industry Policies

Security professionals must:
- Follow employer policies and procedures
- Obtain management approval for research
- Respect client confidentiality
- Maintain professional certifications
- Follow industry codes of ethics

### Government Regulations

Researchers must comply with:
- Export control laws (ITAR, EAR)
- Critical infrastructure protection regulations
- National security requirements
- Data protection laws

---

## Reporting Violations

### If You Observe Misuse

If you become aware of misuse of this framework:

1. **Document** the violation
2. **Report** to appropriate authorities:
   - Law enforcement (if criminal activity)
   - Institutional ethics board
   - Framework maintainers
   - Affected vendors or operators
3. **Do not** confront violators directly
4. **Protect** evidence of violation

### Contact Information

**Framework Maintainers:**
- GitHub: https://github.com/vfg27/EmuOCPP/issues
- Email: [Contact email]

**Law Enforcement:**
- FBI IC3: https://www.ic3.gov
- Local law enforcement
- National cybercrime units

**Industry Contacts:**
- Open Charge Alliance: https://www.openchargealliance.org
- Auto-ISAC: https://www.automotiveisac.com

---

## Acknowledgment

### User Agreement

By using this framework, you acknowledge that:

1. You have read and understood these ethical guidelines
2. You agree to use the framework only for legitimate purposes
3. You will comply with all applicable laws and regulations
4. You will follow responsible disclosure practices
5. You accept full responsibility for your actions
6. You understand the potential consequences of misuse

### Disclaimer

The authors and maintainers of this framework:
- Provide it "as is" without warranty
- Are not responsible for misuse by others
- Reserve the right to revoke access for violations
- May report violations to appropriate authorities

---

## Conclusion

Security research is essential for protecting critical infrastructure and users. By following these ethical guidelines, you contribute to a safer and more secure EV charging ecosystem while maintaining the trust and integrity of the research community.

**Remember:**
- **Think before you act**
- **Get authorization first**
- **Disclose responsibly**
- **Do no harm**
- **Advance security for all**

---

**Questions or Concerns?**

Contact the framework maintainers or consult with:
- Your institutional ethics board
- Legal counsel
- Professional ethics advisors
- Security community mentors

---

**Last Updated:** November 2024

**Version:** 1.0.0

**License:** [To be determined - Research/Academic use]
