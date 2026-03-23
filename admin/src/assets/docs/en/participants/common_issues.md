## Common Issues and Solutions

### "Duplicate participant"

**Problem:** Attempting to add a participant who already exists in the campaign
**Solution:**

- Check the existing participants list
- Verify the identifier is unique within this campaign
- Update existing participant instead of adding new one

### Token not working

**Problem:** Participant reports the survey link doesn't work
**Solution:**

- Verify the token was copied correctly (including the full URL)
- Check that the campaign is still active (not ended)
- Ensure the participant is using the correct link format
- Generate a new participant entry if needed

### Missing demographic data

**Problem:** Need to update participant information after creation
**Solution:**

- Use the edit button to modify participant details
- Add age class, employment rate, or remote work rate
- Save changes to update the participant record

## CSV Export Template

When you download the CSV file, it will contain the following columns:

```csv
identifier,token,url,status,age_class,employment_rate,remote_work_rate,company_vehicle,created_at,updated_at
EMP001,abc123xyz,https://collect.example.com/go/abc123xyz,completed,26-44,100,20,true,2026-01-15T10:33:27.3464322,2026-02-01T14:22:16.456784
EMP002,def456uvw,https://collect.example.com/go/def456uvw,in progress,18-24,80,0,false,2026-02-05T12:18:52.577117,2026-02-05T12:44:05.381780
```

**Columns:**

- **identifier**: Participant's unique identifier from your registry
- **token**: Unique access token for the survey
- **url**: Complete survey URL
- **status**: Current participation status
- **age_class**: Selected age range (if provided)
- **employment_rate**: Employment percentage (if provided)
- **remote_work_rate**: Remote work percentage (if provided)
- **company_vehicle**: Whether participant has company vehicle access (if provided)
- **created_at**: Date at which participant was added
- **updated_at**: Date of the last modification of the participant