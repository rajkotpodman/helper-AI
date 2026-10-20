"""Job Portal Automation Agent Tool for Helper-AI.

Allows the autonomous agent to parse the user's CV from Downloads, create accounts,
and upload resumes across 10 top freelance and work-from-home job portals.
"""
from typing import Dict, Any, Optional
from core.tools.base import BaseTool
from core.job_portal_automation import job_portal_automation


class JobPortalTool(BaseTool):
    """Autonomous Job Portal Registration & CV Upload Tool."""
    name = "job_portal_automation"
    description = (
        "Automates account registration and CV/resume upload across 10 top job portals "
        "(Internshala, Indeed, Naukri, Foundit, Upwork, Freelancer, Wellfound, LinkedIn, Truelancer, Apna) "
        "using the candidate's CV from the Downloads folder. Can parse CV, register portals, and generate reports."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform: 'process_all' (apply to all 10 portals), 'parse_cv' (inspect CV details), 'register_portal' (register on single portal), 'status' (get portals report)",
                "enum": ["process_all", "parse_cv", "register_portal", "status"]
            },
            "portal": {
                "type": "string",
                "description": "Portal name or ID for 'register_portal' action (e.g. 'internshala', 'indeed', 'naukri', 'upwork', 'freelancer', 'wellfound', 'foundit', 'linkedin', 'truelancer', 'apna')."
            },
            "cv_path": {
                "type": "string",
                "description": "Optional custom path to CV or resume file (defaults to finding Jignesh CV in Downloads)."
            }
        },
        "required": ["action"]
    }

    def execute(
        self,
        action: str = "process_all",
        portal: Optional[str] = None,
        cv_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        action_clean = str(action or "process_all").strip().lower()

        if action_clean in ["parse_cv", "get_cv", "read_cv", "extract_cv"]:
            res = job_portal_automation.parse_cv_details(cv_path)
            return {
                "success": res.get("success", False),
                "output": (
                    f"Candidate CV Parsed: {res.get('full_name')} ({res.get('email')} | {res.get('phone')})\n"
                    f"File: {res.get('cv_path')}\n"
                    f"Title: {res.get('title')}\n"
                    f"Skills: {', '.join(res.get('skills', [])[:5])}..."
                ),
                "details": res
            }

        elif action_clean in ["status", "list_portals", "get_status"]:
            portals = job_portal_automation.get_portals()
            lines = [f"Job Portals Status ({len(portals)} portals):"]
            for idx, p in enumerate(portals, start=1):
                cv_stat = "CV Attached" if p.get("cv_uploaded") else "CV Pending"
                lines.append(f"{idx}. {p['name']} ({p['category']}): {p['status']} [{cv_stat}]")
            return {
                "success": True,
                "output": "\n".join(lines),
                "portals": portals
            }

        elif action_clean in ["register_portal", "single_portal", "apply_portal"]:
            portal_id = (portal or kwargs.get("portal_id") or "internshala").lower()
            res = job_portal_automation.register_and_upload(portal_id, cv_path)
            return {
                "success": res.get("success", False),
                "output": f"Portal '{res.get('portal')}': Status: {res.get('status')}. CV uploaded: {res.get('cv_uploaded')}. Notes: {', '.join(res.get('notes', []))}",
                "result": res
            }

        elif action_clean in ["process_all", "apply_all", "all_portals", "execute_all"]:
            res = job_portal_automation.process_all_10_portals(cv_path)
            return {
                "success": res.get("success", False),
                "output": (
                    f"Autonomous Job Portal Processing Complete for candidate '{res.get('candidate')}'!\n"
                    f"Portals Processed: {res.get('portals_processed')}/10.\n"
                    f"Verified CV: {res.get('cv_path')}\n"
                    f"Full executive report written to: {res.get('report_path')}"
                ),
                "details": res
            }

        elif action_clean in ["enter_otp", "submit_otp", "verify_otp", "input_otp"]:
            otp_code = str(kwargs.get("otp") or kwargs.get("code") or portal or "").strip()
            res = job_portal_automation.enter_otp(otp_code, portal)
            return {
                "success": res.get("success", False),
                "output": res.get("message", "OTP processed."),
                "details": res
            }

        else:
            return {"success": False, "output": f"Unknown action: '{action}'. Choose from 'process_all', 'parse_cv', 'register_portal', 'status', 'enter_otp'."}
