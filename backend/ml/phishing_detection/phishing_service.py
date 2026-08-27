from ml.phishing_detection.url_analyzer import (
    extract_url_features
)


class PhishingDetectionService:

    def analyze(self, url: str):

        analysis = extract_url_features(url)

        features = analysis["features"]

        score = 0.0
        reasons = []

        if not features["https"]:
            score += 15
            reasons.append(
                "URL does not use HTTPS."
            )

        if features["is_ip_address"]:
            score += 30
            reasons.append(
                "URL uses an IP address instead of a domain name."
            )

        if features["has_at_symbol"]:
            score += 25
            reasons.append(
                "URL contains an @ symbol that may obscure the destination."
            )

        if features["url_length"] >= 150:
            score += 15
            reasons.append(
                "URL is unusually long."
            )

        elif features["url_length"] >= 100:
            score += 8
            reasons.append(
                "URL is longer than typical."
            )

        if features["subdomain_count"] >= 4:
            score += 15
            reasons.append(
                "URL contains an unusually large number of subdomains."
            )

        elif features["subdomain_count"] >= 3:
            score += 8
            reasons.append(
                "URL contains multiple subdomains."
            )

        if features["suspicious_keyword_count"] >= 3:
            score += 20
            reasons.append(
                "URL contains multiple security-sensitive keywords."
            )

        elif features["suspicious_keyword_count"] >= 1:
            score += 8
            reasons.append(
                "URL contains security-sensitive keywords."
            )

        if features["suspicious_tld"]:
            score += 20
            reasons.append(
                "Domain uses a TLD frequently associated with suspicious URLs."
            )

        if features["has_punycode"]:
            score += 25
            reasons.append(
                "Domain contains punycode that may indicate an impersonation domain."
            )

        if features["has_percent_encoding"]:
            score += 8
            reasons.append(
                "URL contains encoded characters."
            )

        if features["has_double_slash_path"]:
            score += 10
            reasons.append(
                "URL contains an unusual double-slash path."
            )

        score = round(
            min(score, 100),
            2
        )

        if score >= 70:
            status = "MALICIOUS"
        elif score >= 40:
            status = "SUSPICIOUS"
        else:
            status = "LOW_RISK"

        if not reasons:
            reasons.append(
                "No obvious phishing indicators were detected by the local scanner."
            )

        return {
            "url": url,
            "domain": analysis["hostname"],
            "risk_score": score,
            "status": status,
            "indicators": reasons,
            "matched_keywords": analysis[
                "keyword_matches"
            ],
            "features": features,
            "disclaimer": (
                "This local analysis is a risk indicator, "
                "not proof that a website is safe or malicious."
            )
        }


phishing_service = PhishingDetectionService()
