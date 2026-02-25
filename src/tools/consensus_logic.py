# import numpy as np

# def calculate_consensus_verdict(ml_result, web_results, rag_results):
#     """
#     ml_result: {'prediction': 'P2463', 'confidence': 0.65}
#     web_results: List of {'source': 'Team-BHP', 'relevance': 0.8, 'is_official': True}
#     rag_results: List of snippets from AstraDB/PDF
#     """
    
#     # 1. Base ML Score
#     ml_score = ml_result['confidence']
#     verdict_dtc = ml_result['prediction']
    
#     # 2. Calculate Web Score with Authority Bonus
#     web_scores = []
#     for site in web_results:
#         score = site['relevance']
#         # Apply your +5% Authority Bonus
#         if site.get('is_official', False) or "team-bhp" in site['source'].lower():
#             score += 0.05
#         web_scores.append(score)
    
#     avg_web_score = np.mean(web_scores) if web_scores else 0
    
#     # 3. Decision Logic
#     final_verdict = ""
#     reasoning = ""
    
#     if ml_score >= 0.70:
#         final_verdict = verdict_dtc
#         reasoning = f"Fast Brain confirmed {verdict_dtc} with high confidence (${ml_score*100:.1f}\%$)."
#     elif avg_web_score > ml_score:
#         final_verdict = verdict_dtc # Usually the web search is confirming the code found
#         reasoning = f"ML was uncertain (${ml_score*100:.1f}\%$), but High-Authority Web Search (${avg_web_score*100:.1f}\%$) confirmed the symptom patterns."
#     else:
#         final_verdict = "UNCERTAIN"
#         reasoning = "Consensus could not be reached. Manual inspection of wiring and ground points recommended."

#     return {
#         "verdict": final_verdict,
#         "reasoning": reasoning,
#         "ml_contribution": ml_score,
#         "web_contribution": avg_web_score
#     }


import numpy as np

def calculate_consensus_verdict(ml_result, web_results, rag_results):
    """
    ml_result: {'prediction': 'P2463', 'confidence': 0.65}
    web_results: List of {'url': '...', 'content': '...'} or dictionaries containing 'source'/'url' and 'relevance'
    rag_results: List of snippets from AstraDB/PDF
    """
    
    # 1. Base ML Score
    ml_score = ml_result.get('confidence', 0.0)
    verdict_dtc = ml_result.get('prediction', 'Unknown')
    
    # 2. Define Trusted Domains
    trusted_domains = [
        "team-bhp.com", 
        "mechanics.stackexchange.com", 
        "nhtsa.gov",
        "obd-codes.com",
        "repairpal.com"
    ]
    
    # 3. Calculate Web Score with Authority Bonus
    web_scores = []
    
    # Check if web_results is valid and iterable
    if isinstance(web_results, list):
        for site in web_results:
            # We assign a base relevance if the search engine didn't provide one
            # (Tavily often returns just 'url' and 'content')
            score = site.get('relevance', 0.5) 
            
            # Determine the source URL to check against our trusted list
            # We check both 'url' and 'source' depending on how the data is passed
            source_url = site.get('url', site.get('source', '')).lower()
            
            # Apply your +10% Authority Bonus if it's in the trusted list
            for domain in trusted_domains:
                if domain in source_url:
                    score += 0.10 # Give it a 10% boost for being a highly valid source!
                    break # Stop checking once we find a match
            
            # Apply an official bonus if explicitly marked
            if site.get('is_official', False):
                score += 0.05
                
            web_scores.append(score)
    
    # Calculate the average web score
    avg_web_score = np.mean(web_scores) if web_scores else 0.0
    
    # 4. Decision Logic
    final_verdict = ""
    reasoning = ""
    
    if ml_score >= 0.70:
        final_verdict = verdict_dtc
        reasoning = f"Fast Brain confirmed {verdict_dtc} with high confidence ({ml_score*100:.1f}%)."
    elif avg_web_score > ml_score:
        final_verdict = verdict_dtc # Usually the web search is confirming the code found
        reasoning = f"ML was uncertain ({ml_score*100:.1f}%), but High-Authority Web Search ({avg_web_score*100:.1f}%) confirmed the issue."
    elif len(rag_results) > 0:
         final_verdict = "Pending Manual Review"
         reasoning = "ML and Web were inconclusive. Relying strictly on official manual documentation."
    else:
        final_verdict = "Unknown"
        reasoning = "Insufficient data to reach a confident consensus."
        
    return {
        "verdict": final_verdict,
        "reasoning": reasoning,
        "ml_confidence": float(ml_score),
        "web_confidence": float(avg_web_score)
    }
