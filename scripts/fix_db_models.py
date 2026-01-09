import os
import glob

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 1. Fix imports
    # Handle composite import first
    if "from sqlalchemy.dialects.postgresql import UUID, JSONB" in content:
        content = content.replace(
            "from sqlalchemy.dialects.postgresql import UUID, JSONB", 
            "from sqlalchemy import Uuid as UUID, JSON as JSONB"
        )
    elif "from sqlalchemy.dialects.postgresql import JSONB, UUID" in content:
         content = content.replace(
            "from sqlalchemy.dialects.postgresql import JSONB, UUID", 
            "from sqlalchemy import JSON as JSONB, Uuid as UUID"
        )
    
    # Handle single imports
    content = content.replace("from sqlalchemy.dialects.postgresql import UUID", "from sqlalchemy import Uuid as UUID")
    content = content.replace("from sqlalchemy.dialects.postgresql import JSONB", "from sqlalchemy import JSON as JSONB")
    
    # 2. Fix usage
    # standard SQLAlchemy Uuid type handles uuids natively, doesn't need as_uuid=True
    content = content.replace("UUID(as_uuid=True)", "UUID")
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Fixed {filepath}")

models_dir = "app/models"
for filepath in glob.glob(os.path.join(models_dir, "*.py")):
    fix_file(filepath)
