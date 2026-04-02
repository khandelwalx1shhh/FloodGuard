import subprocess
import json
from datetime import datetime
import os

class DefenseSelector:
    def __init__(self):
        self.defense_log_path = r"d:\CyberProject\V2\backend\logs\defense_actions.json"
        self.blocked_ips = set()
        self.rate_limited_ips = {}
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.defense_log_path), exist_ok=True)
    
    def select_defense(self, threat_score, traffic_features):
        """Select appropriate defense based on threat score and traffic patterns"""
        if threat_score > 0.8:
            return self.block_ip(traffic_features)
        elif threat_score > 0.5:
            return self.apply_rate_limiting(traffic_features)
        elif threat_score > 0.3:
            return self.increase_monitoring(traffic_features)
        return "No action needed"

    def block_ip(self, traffic_features):
        """Block malicious IP using Windows Firewall"""
        ip = traffic_features.get('source_ip', '')
        if ip and ip not in self.blocked_ips:
            try:
                # Add Windows Firewall rule
                rule_name = f"DDoS_Block_{ip}"
                command = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip}'
                subprocess.run(command, shell=True, check=True)
                
                self.blocked_ips.add(ip)
                self._log_action("ip_block", ip, traffic_features)
                return f"Blocked IP: {ip}"
            except subprocess.CalledProcessError as e:
                return f"Failed to block IP: {str(e)}"
        return "IP already blocked or invalid"

    def apply_rate_limiting(self, traffic_features):
        """Apply rate limiting using Windows Advanced Firewall"""
        ip = traffic_features.get('source_ip', '')
        if ip and ip not in self.rate_limited_ips:
            try:
                # Add rate limiting rule
                rule_name = f"DDoS_RateLimit_{ip}"
                command = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=allow remoteip={ip} enable=yes'
                subprocess.run(command, shell=True, check=True)
                
                self.rate_limited_ips[ip] = datetime.now()
                self._log_action("rate_limit", ip, traffic_features)
                return f"Applied rate limiting to IP: {ip}"
            except subprocess.CalledProcessError as e:
                return f"Failed to apply rate limiting: {str(e)}"
        return "IP already rate limited or invalid"

    def increase_monitoring(self, traffic_features):
        """Increase monitoring frequency for suspicious traffic"""
        ip = traffic_features.get('source_ip', '')
        self._log_action("increased_monitoring", ip, traffic_features)
        return f"Increased monitoring for IP: {ip}"

    def _log_action(self, action_type, ip, traffic_features):
        """Log defense actions"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "ip": ip,
            "traffic_features": traffic_features
        }
        
        try:
            # Load existing logs
            if os.path.exists(self.defense_log_path):
                with open(self.defense_log_path, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new log entry
            logs.append(log_entry)
            
            # Save updated logs
            with open(self.defense_log_path, 'w') as f:
                json.dump(logs, f, indent=4)
        except Exception as e:
            print(f"Failed to log defense action: {str(e)}")