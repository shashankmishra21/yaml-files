import os
import re
import time
import json

def safe_str(value):
    """Safely convert any value to string"""
    if isinstance(value, list):
        return str(value[0]) if value else ""
    elif value is None:
        return ""
    else:
        return str(value)

def safe_strip(value):
    """Safely strip any value"""
    return safe_str(value).strip()

class UltraRobustWorkflowRunner:
    def __init__(self, workflow_file):
        self.workflow_file = workflow_file
        self.workflow = {}
        self.steps = []
        self.parse_workflow()
        
    def parse_workflow(self):
        """Parse workflow file line by line to avoid all YAML issues"""
        print("🔍 Debug: Starting workflow parsing...")
        
        with open(self.workflow_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Process each line safely
        for line_num, line in enumerate(lines, 1):
            try:
                line = safe_strip(line)
                
                if line.startswith('path:'):
                    path_value = line.split(':', 1)[1] if ':' in line else ""
                    self.workflow['path'] = safe_strip(path_value)
                    print(f"   ✓ Found path: {self.workflow['path']}")
                    
                elif line.startswith('method:'):
                    method_value = line.split(':', 1) if ':' in line else ""
                    self.workflow['method'] = safe_strip(method_value)
                    print(f"   ✓ Found method: {self.workflow['method']}")
                    
                elif 'message:' in line and 'response' not in line:
                    message_part = line.split('message:', 1) if 'message:' in line else ""
                    message = safe_strip(message_part).strip('"\'')
                    if 'response' not in self.workflow:
                        self.workflow['response'] = {}
                    self.workflow['response']['message'] = message
                    print(f"   ✓ Found message: {message}")
                    
                elif 'statusCode:' in line:
                    status_part = line.split('statusCode:', 1)[1] if 'statusCode:' in line else "200"
                    try:
                        status = int(safe_strip(status_part))
                        if 'response' not in self.workflow:
                            self.workflow['response'] = {}
                        self.workflow['response']['statusCode'] = status
                        print(f"   ✓ Found statusCode: {status}")
                    except ValueError:
                        print(f"   ⚠️  Invalid statusCode on line {line_num}: {status_part}")
                        
                elif '!include' in line:
                    # Extract include path very carefully
                    include_match = re.search(r'!include\s+(.+)', line)
                    if include_match:
                        include_path = safe_strip(include_match.group(1))
                        
                        # Clean up path
                        if '?' in include_path:
                            include_path = include_path.split('?')[0]
                        if include_path.startswith('file:'):
                            include_path = include_path[5:].strip()
                        
                        step_info = {
                            'number': len(self.steps) + 1,
                            'include_path': include_path,
                            'line_number': line_num
                        }
                        self.steps.append(step_info)
                        print(f"   ✓ Found include: {include_path}")
                        
            except Exception as e:
                print(f"   ⚠️  Error on line {line_num}: {e}")
                continue
                
        print(f"🎯 Parsing complete: Found {len(self.steps)} steps")
            
    def run_workflow(self):
        """Execute the workflow simulation"""
        print(f"\n🚀 Starting workflow: {self.workflow.get('path', 'Unknown')}")
        print(f"📝 Method: {self.workflow.get('method', 'Unknown')}")
        print(f"🎯 Total Steps: {len(self.steps)}")
        print("=" * 60)
        
        for step in self.steps:
            self.execute_step(step)
            
        return self.build_response()
    
    def execute_step(self, step_info):
        """Execute individual step with maximum safety"""
        step_number = step_info['number']
        include_path = safe_str(step_info['include_path'])
        
        print(f"\n🔄 Step {step_number}: Processing")
        print(f"   📁 File: {include_path}")
        print(f"   📍 From line: {step_info['line_number']}")
        
        if not include_path:
            print(f"   ❌ Empty include path")
            return
            
        if os.path.exists(include_path):
            try:
                self.load_and_simulate_step(include_path)
            except Exception as e:
                print(f"   ❌ Error loading step: {e}")
        else:
            print(f"   ⚠️  File not found: {include_path}")
            
    def load_and_simulate_step(self, include_path):
        """Load step file safely without YAML parsing"""
        with open(include_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract step info safely
        step_info = {}
        
        for line in content.split('\n'):
            line = safe_strip(line)
            if line.startswith('id:'):
                step_info['id'] = safe_strip(line.split(':', 1)[1])
            elif line.startswith('name:'):
                step_info['name'] = safe_strip(line.split(':', 1))
            elif line.startswith('type:'):
                step_info['type'] = safe_strip(line.split(':', 1))
            elif line.startswith('desc:'):
                desc_part = line.split(':', 1) if ':' in line else ""
                step_info['desc'] = safe_strip(desc_part).strip('"\'')
        
        # Display step info
        print(f"   🏷️  ID: {step_info.get('id', 'unknown')}")
        print(f"   📝 Name: {step_info.get('name', 'unnamed')}")
        print(f"   🏗️  Type: {step_info.get('type', 'generic')}")
        print(f"   📄 Description: {step_info.get('desc', 'No description')}")
        
        # Simulate execution
        step_type = step_info.get('type', 'generic')
        if step_type == 'business':
            print(f"   🔧 Executing business logic...")
            time.sleep(0.5)
            print(f"   ✅ Business logic completed")
        elif step_type == 'db':
            print(f"   🗄️  Executing database operation...")
            time.sleep(1.0)
            print(f"   ✅ Database operation completed")
        elif step_type == 'vendor':
            print(f"   🌐 Executing vendor API call...")
            time.sleep(1.5)
            print(f"   ✅ Vendor API call completed")
        else:
            print(f"   ⚙️  Executing generic step...")
            time.sleep(0.3)
            print(f"   ✅ Generic step completed")
            
    def build_response(self):
        """Build final response"""
        response = self.workflow.get('response', {})
        return {
            "message": response.get('message', 'Workflow completed'),
            "statusCode": response.get('statusCode', 200),
            "executionTime": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stepsExecuted": len(self.steps),
            "workflowPath": self.workflow.get('path', 'Unknown'),
            "method": self.workflow.get('method', 'Unknown')
        }

def main():
    """Main execution function"""
    workflow_file = 'routes/fetch_br.yaml'
    
    print("🚀 Ultra-Robust YAML Workflow Runner")
    print("=" * 60)
    
    # Check if workflow file exists
    if not os.path.exists(workflow_file):
        print(f"❌ Workflow file not found: {workflow_file}")
        print("\nCurrent directory contents:")
        try:
            for item in os.listdir('.'):
                print(f"    📄 {item}")
        except:
            print("    Cannot list directory contents")
        return
    
    try:
        # Create and run workflow
        runner = UltraRobustWorkflowRunner(workflow_file)
        result = runner.run_workflow()
        
        # Display results
        print('\n' + '=' * 60)
        print('🎉 Workflow Execution Completed Successfully!')
        print('📊 Final Result:')
        print(json.dumps(result, indent=2))
        
    except Exception as error:
        print(f'\n❌ Workflow Execution Failed!')
        print(f'Error: {error}')
        print(f'Error Type: {type(error).__name__}')
        
        # More detailed debugging
        import traceback
        print(f'\n📋 Full Error Traceback:')
        traceback.print_exc()

if __name__ == "__main__":
    main()