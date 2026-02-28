import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import Base, engine, SessionLocal, Operator, Procedure, ProcedureOperator, IrradiationEvent, VideoFrame, TeachingFile, AnatomicGrid
import random
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Check if already seeded
if db.query(Operator).count() > 0:
    print("Already seeded, skipping")
    db.close()
    sys.exit(0)

random.seed(42)

# Operators
OPERATORS = [
    ("James Duncan", "attending", "Interventional Radiology"),
    ("Sarah Mitchell", "attending", "Interventional Radiology"),
    ("Robert Chen", "attending", "Interventional Radiology"),
    ("Maria Gonzalez", "attending", "Interventional Radiology"),
    ("David Kim", "attending", "Neurointerventional"),
    ("Lisa Thompson", "fellow", "Interventional Radiology"),
    ("Michael Park", "fellow", "Interventional Radiology"),
    ("Jennifer Wang", "fellow", "Neurointerventional"),
    ("Andrew Foster", "resident", "Diagnostic Radiology"),
    ("Emily Cruz", "resident", "Diagnostic Radiology"),
    ("Thomas Wright", "resident", "Diagnostic Radiology"),
    ("Rachel Adams", "pa", "Interventional Radiology"),
    ("Kevin O'Brien", "pa", "Interventional Radiology"),
    ("Amanda Lee", "tech", "Interventional Radiology"),
    ("Christopher Hall", "tech", "Interventional Radiology"),
]
ops = []
for i, (name, role, spec) in enumerate(OPERATORS):
    op = Operator(id=i+1, name=name, role=role, specialty=spec, npi=f"1234567{i:03d}", is_active=True)
    db.add(op)
    ops.append(op)
db.flush()

# Procedure templates
PROCS = [
    ("Diagnostic Angiogram - Lower Extremity", "vascular", "diagnostic", "Common femoral artery", "Lower extremity"),
    ("Diagnostic Angiogram - Renal", "vascular", "diagnostic", "Common femoral artery", "Renal arteries"),
    ("TIPS Creation", "vascular", "interventional", "Right internal jugular vein", "Hepatic/portal vein"),
    ("TIPS Revision", "vascular", "interventional", "Right internal jugular vein", "TIPS stent"),
    ("Hepatic Chemoembolization", "vascular", "interventional", "Common femoral artery", "Hepatic artery"),
    ("Uterine Fibroid Embolization", "vascular", "interventional", "Common femoral artery", "Uterine arteries"),
    ("Port-a-Cath Placement", "vascular", "interventional", "Right internal jugular vein", "SVC"),
    ("PICC Line Placement", "vascular", "interventional", "Basilic vein", "SVC"),
    ("Tunneled Dialysis Catheter", "vascular", "interventional", "Right internal jugular vein", "Right atrium"),
    ("Nephrostomy Tube Placement", "gu", "interventional", "Posterior flank", "Renal pelvis"),
    ("Biliary Drain Placement", "gi", "interventional", "Right anterior chest wall", "Common bile duct"),
    ("IVC Filter Placement", "vascular", "interventional", "Common femoral vein", "Infrarenal IVC"),
    ("IVC Filter Retrieval", "vascular", "interventional", "Right internal jugular vein", "Infrarenal IVC"),
    ("Lower Extremity Angioplasty/Stent", "vascular", "interventional", "Common femoral artery", "SFA/popliteal"),
    ("Dialysis Fistulogram", "vascular", "diagnostic", "Fistula/graft", "AV fistula"),
    ("Percutaneous Abscess Drainage", "gi", "interventional", "Varies", "Abscess cavity"),
    ("Thoracentesis", "pulmonary", "interventional", "Posterior chest wall", "Pleural space"),
    ("Paracentesis", "gi", "interventional", "Left lower quadrant", "Peritoneal cavity"),
    ("Transjugular Liver Biopsy", "gi", "interventional", "Right internal jugular vein", "Hepatic vein"),
    ("Bone Biopsy", "musculoskeletal", "interventional", "Varies", "Bone lesion"),
    ("Cardiac Catheterization", "cardiac", "diagnostic", "Common femoral artery", "Coronary arteries"),
    ("Coronary Angioplasty/Stent", "cardiac", "interventional", "Common femoral artery", "Coronary arteries"),
    ("Cerebral Angiogram", "neuro", "diagnostic", "Common femoral artery", "Cerebral vasculature"),
    ("Mechanical Thrombectomy - Stroke", "neuro", "interventional", "Common femoral artery", "MCA/ICA"),
    ("Lumbar Puncture", "neuro", "interventional", "L3-L4 interspace", "Thecal sac"),
]

INDICATIONS = [
    "Abnormal CT findings concerning for vascular pathology",
    "Worsening renal function with suspected renal artery stenosis",
    "Recurrent GI bleeding, evaluate for embolization",
    "Symptomatic uterine fibroids refractory to medical therapy",
    "Need for long-term IV access for chemotherapy",
    "Acute DVT with threatened limb",
    "Rising bilirubin with biliary obstruction on imaging",
    "Large pleural effusion causing respiratory compromise",
    "Suspected hepatocellular carcinoma for locoregional therapy",
    "Critical limb ischemia with non-healing wound",
]

FINDINGS_TEMPLATES = [
    "Successful {} performed without complication. Adequate hemostasis achieved.",
    "Procedure completed successfully. {} demonstrated with appropriate treatment.",
    "{} completed. Post-procedure imaging confirms satisfactory positioning.",
    "Technically successful {}. No immediate complications noted.",
]

# Anatomic grids (29 locations from Swin Transformer)
GRIDS = [
    (1, "Right upper chest", "thorax"), (2, "Left upper chest", "thorax"),
    (3, "Right mid chest", "thorax"), (4, "Left mid chest", "thorax"),
    (5, "Right lower chest", "thorax"), (6, "Left lower chest", "thorax"),
    (7, "Right upper abdomen", "abdomen"), (8, "Left upper abdomen", "abdomen"),
    (9, "Right mid abdomen", "abdomen"), (10, "Epigastric", "abdomen"),
    (11, "Left mid abdomen", "abdomen"), (12, "Right lower abdomen", "abdomen"),
    (13, "Periumbilical", "abdomen"), (14, "Left lower abdomen", "abdomen"),
    (15, "Right pelvis", "pelvis"), (16, "Central pelvis", "pelvis"),
    (17, "Left pelvis", "pelvis"), (18, "Right hip", "extremity"),
    (19, "Left hip", "extremity"), (20, "Right upper thigh", "extremity"),
    (21, "Left upper thigh", "extremity"), (22, "Right knee", "extremity"),
    (23, "Left knee", "extremity"), (24, "Right lower leg", "extremity"),
    (25, "Left lower leg", "extremity"), (26, "Cervical spine", "spine"),
    (27, "Thoracic spine", "spine"), (28, "Lumbar spine", "spine"),
    (29, "Head/cranium", "neuro"),
]
for gn, label, region in GRIDS:
    db.add(AnatomicGrid(grid_number=gn, label=label, body_region=region))
db.flush()

# Generate 500 procedures
base_date = datetime(2020, 1, 1)
for i in range(500):
    proc_template = random.choice(PROCS)
    proc_date = base_date + timedelta(days=random.randint(0, 2200))
    hour = random.randint(7, 17)
    minute = random.randint(0, 59)
    start = proc_date.replace(hour=hour, minute=minute)
    dur = random.randint(15, 180)
    end = start + timedelta(minutes=dur)
    fluoro_time = random.uniform(30, dur * 40)
    total_dap = random.uniform(50, 5000)
    total_ak = random.uniform(100, 8000)
    n_events = random.randint(3, 20)

    p = Procedure(
        accession_number=f"BJH-{2020 + i // 100}-{i:06d}",
        procedure_name=proc_template[0],
        procedure_date=proc_date,
        room_number=random.randint(1, 10),
        category=proc_template[1],
        subcategory=proc_template[2],
        access_site=proc_template[3],
        target_site=proc_template[4],
        start_time=start,
        end_time=end,
        duration_minutes=dur,
        fluoroscopy_time_seconds=fluoro_time,
        total_dap=round(total_dap, 2),
        total_air_kerma=round(total_ak, 2),
        total_frames=n_events * random.randint(1, 5),
        patient_age=random.randint(18, 92),
        patient_sex=random.choice(["M", "F"]),
        patient_bmi=round(random.uniform(18.5, 45.0), 1),
        dictated_report=random.choice(FINDINGS_TEMPLATES).format(proc_template[0]),
        indication=random.choice(INDICATIONS),
        findings=f"See dictated report for details of {proc_template[0].lower()}.",
        complications=random.choice(["None", "None", "None", "Minor bleeding at access site", "Transient vasospasm"]),
        primary_operator_id=random.choice([1,2,3,4,5]),
        video_path=f"/data/videos/{proc_date.strftime('%Y/%m/%d')}/room{random.randint(1,10)}/{i:06d}.mp4",
        teaching_status=random.choice(["unscreened"]*8 + ["flagged", "approved"]),
    )
    db.add(p)
    db.flush()

    # Secondary operators
    if random.random() > 0.3:
        trainee = random.choice([6,7,8,9,10,11])
        db.add(ProcedureOperator(procedure_id=p.id, operator_id=trainee, role=ops[trainee-1].role))

    # Irradiation events
    for j in range(n_events):
        evt_time = start + timedelta(seconds=j * (dur * 60 / n_events))
        grid = random.choice(GRIDS)
        ie = IrradiationEvent(
            procedure_id=p.id,
            event_number=j + 1,
            acquisition_protocol=random.choice(["Fluoro Low", "Fluoro Standard", "Fluoro High", "DSA", "Acquisition"]),
            image_type=random.choice(["fluoroscopy", "fluoroscopy", "fluoroscopy", "acquisition", "DSA"]),
            primary_angle=round(random.uniform(-40, 40), 1),
            secondary_angle=round(random.uniform(-30, 30), 1),
            table_longitude=round(random.uniform(-20, 20), 1),
            table_latitude=round(random.uniform(-15, 15), 1),
            dap=round(total_dap / n_events * random.uniform(0.5, 1.5), 2),
            air_kerma=round(total_ak / n_events * random.uniform(0.5, 1.5), 2),
            kvp=random.choice([70, 75, 80, 85, 90, 100, 110, 120]),
            ma=round(random.uniform(1, 10), 1),
            duration_ms=round(random.uniform(100, 5000), 0),
            event_datetime=evt_time,
            task_label=random.choice(["Wire navigation", "Contrast injection", "Catheter positioning", "Stent deployment", "Balloon inflation", "Coil deployment", "Imaging survey"]),
            anatomic_region=grid[2],
        )
        db.add(ie)
        db.flush()

        # Frame for ~40% of events
        if random.random() > 0.6:
            db.add(VideoFrame(
                procedure_id=p.id,
                irradiation_event_id=ie.id,
                frame_number=j,
                timestamp_seconds=j * (dur * 60 / n_events),
                file_path=f"/data/frames/{p.accession_number}/frame_{j:04d}.jpg",
                anatomic_grid=grid[0],
                anatomic_grid_label=grid[1],
                grid_confidence=round(random.uniform(0.75, 0.99), 3),
                task_detected=ie.task_label,
                body_part=grid[2],
            ))

db.commit()

# Teaching files
procs = db.query(Procedure).filter(Procedure.teaching_status != "unscreened").limit(20).all()
for i, proc in enumerate(procs):
    status = random.choice(["draft", "screened", "approved", "published"])
    db.add(TeachingFile(
        procedure_id=proc.id,
        title=f"Teaching Case: {proc.procedure_name}",
        description=f"Educational case demonstrating {proc.procedure_name.lower()} technique.",
        category=random.choice(["routine", "problem-solving", "complication"]),

        status=status,
        view_count=random.randint(0, 500) if status == "published" else 0,
        avg_rating=round(random.uniform(3.5, 5.0), 1) if status == "published" else None,
        youtube_url="https://youtu.be/HiIyAKw0Ho8" if status == "published" else None,
    ))
db.commit()
db.close()

print("Seeded:")
print(f"  - 15 operators")
print(f"  - 500 procedures")
print(f"  - 29 anatomic grids")
print(f"  - 20 teaching files")
print("  - ~5000+ irradiation events")
print("  - ~2000 video frames")
