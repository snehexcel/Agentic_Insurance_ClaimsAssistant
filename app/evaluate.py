from datetime import date
from .workflow import process_claim

def evaluation_cases():
    today=date.today().isoformat()
    return [
      {"name":"complete_auto_claim","claim":{"claimant_name":"Asha Verma","policy_number":"POL-1001","claim_type":"auto","incident_description":"Rear bumper damage after a low-speed collision in a parking area.","claimed_amount":1800,"incident_date":today,"documents_provided":["incident_report","repair_estimate"]},"expected_route":"human_review","expected_flag":False},
      {"name":"missing_auto_documents","claim":{"claimant_name":"Ravi Kumar","policy_number":"POL-1002","claim_type":"auto","incident_description":"Front door damage after another vehicle scraped the car.","claimed_amount":900,"incident_date":today,"documents_provided":[]},"expected_route":"needs_information","expected_flag":True},
      {"name":"high_amount_home_claim","claim":{"claimant_name":"Mira Das","policy_number":"POL-2001","claim_type":"home","incident_description":"Water damage to kitchen cabinets following a pipe leak.","claimed_amount":40000,"incident_date":today,"documents_provided":["photos","repair_estimate"]},"expected_route":"human_review","expected_flag":True}]

def run_evaluation():
    results=[]; routes_ok=0; flags_ok=0
    for case in evaluation_cases():
        result=process_claim(case["claim"]); route_ok=result.get("route")==case["expected_route"]
        flag_ok=bool(result.get("validation_flags"))==case["expected_flag"]
        routes_ok += int(route_ok); flags_ok += int(flag_ok)
        results.append({"case":case["name"],"expected_route":case["expected_route"],"actual_route":result.get("route"),"route_correct":route_ok,"expected_flag_present":case["expected_flag"],"actual_flags":result.get("validation_flags",[]),"flag_check_correct":flag_ok})
    total=len(results)
    return {"total_cases":total,"route_accuracy":round(routes_ok/total,3),"expected_flag_recall":round(flags_ok/total,3),"results":results}

if __name__ == "__main__":
    import json
    print(json.dumps(run_evaluation(), indent=2))
