import yaml
import json
import time
import os
import re

class SimpleWorkflowRunner:
    def __init__(self, workflow_file):
        self.workflow_file = workflow_file
        self.workflow = {}
        self.steps = []
        self.parse_workflow()
        
    def parse_workflow(self):
        """Parse workflow file manually to avoid YAML include issues"""
        with open(self.workflow_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract basic workflow info
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('path:'):
                self.workflow['path'] = line.split(':', 1)[1].strip()
            elif line.startswith('method:'):
                self.workflow['method'] = line.split(':', 1).strip()
            elif 'message:' in line and 'response:' not in line:
                message = line.split('message:', 1).strip().strip('"\'')
                if 'response' not in self.workflow:
                    self.workflow['response'] = {}
                self.workflow['response']['message'] = message
            elif 'statusCode:' in line:
                status = line.split('statusCode:', 1)[1].strip()
                if 'response' not in self.workflow:
                    self.workflow['response'] = {}
                self.workflow['response']['statusCode'] = int(status)
        
        # Find include statements using regex
        include_pattern = r'- !include\s+([^\s]+)'
        includes = re.findall(include_pattern, content)
        
        step_count = 1
        for include_path in includes:
            # Clean up include path
            clean_path = include_path.strip()
            if '?' in clean_path:
                clean_path = clean_path.split('?')[0]
            if clean_path.startswith('file:'):
                clean_path = clean_path[5:].strip()
            
            step_info = {
                'number': step_count,
                'include_path': clean_path,
                'original_path': include_path
            }
            self.steps.append(step_info)
            step_count += 1
            
    def run_workflow(self):
        """Execute the workflow simulation"""
        print(f"🚀 Starting workflow: {self.workflow.get('path', 'Unknown')}")
        print(f"📝 Method: {self.workflow.get('method', 'Unknown')}")
        print(f"🎯 Total Steps Found: {len(self.steps)}")
        print("=" * 60)
        
        for step in self.steps:
            self.execute_step(step)
            
        return self.build_response()
    
    def execute_step(self, step_info):
        """Execute individual step"""
        step_number = step_info['number']
        include_path = step_info['include_path']
        
        print(f"\n🔄 Step {step_number}: Processing")
        print(f"   📁 File: {include_path}")
        
        if os.path.exists(include_path):
            try:
                # Load step file content
                with open(include_path, 'r', encoding='utf-8') as f:
                    step_content = yaml.safe_load(f)
                
                if step_content:
                    self.simulate_step_execution(step_content)
                else:
                    print(f"   ⚠️  Empty step file")
                    
            except Exception as e:
                print(f"   ❌ Error loading step: {e}")
        else:
            print(f"   ⚠️  File not found: {include_path}")
            
    def simulate_step_execution(self, step_content):
        """Simulate step execution based on content"""
        step_id = step_content.get('id', 'unknown')
        step_name = step_content.get('name', 'unnamed')
        step_type = step_content.get('type', 'generic')
        step_desc = step_content.get('desc', 'No description')
        
        print(f"   🏷️  ID: {step_id}")
        print(f"   📝 Name: {step_name}")
        print(f"   🏗️  Type: {step_type}")
        print(f"   📄 Description: {step_desc}")
        
        # Simulate execution based on type
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
            
        # Check for branches
        if 'branches' in step_content:
            branches = step_content['branches']
            print(f"   🔀 Branches configured: {branches}")
            
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
    
    print("🚀 YAML Workflow Runner (Fixed Version)")
    print("=" * 60)
    
    # Check if workflow file exists
    if not os.path.exists(workflow_file):
        print(f"❌ Workflow file not found: {workflow_file}")
        print("\nPlease ensure you have:")
        print("  ✓ routes/fetch_br.yaml (main workflow file)")
        print("  ✓ steps/ directory with all step files")
        print("\nCurrent directory contents:")
        try:
            files = os.listdir('.')
            for f in files:
                print(f"    - {f}")
        except Exception as e:
            print(f"    Error listing files: {e}")
        return
    
    try:
        # Create and run workflow
        runner = SimpleWorkflowRunner(workflow_file)
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
        
        print("\n🔧 Troubleshooting Tips:")
        print("1. Check YAML file syntax and indentation")
        print("2. Verify all include file paths exist")
        print("3. Ensure no tabs in YAML files (use spaces only)")
        print("4. Check file permissions")

if __name__ == "__main__":
    main()
