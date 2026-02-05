## Participants Management

Participants are employees or members of a company who complete mobility surveys within a campaign. Each campaign maintains its own list of participants identified by a unique identifier that references the company's external participant registry.

### Adding Participants

Participants are added manually through the campaign's participants section:

1. Navigate to the campaign's participants section
2. Click "Add" button
3. Enter the participant information:
   - **Identifier** (_required_): A unique identifier that references your company's external participant registry (e.g., employee ID, badge number)
   - **Age Class** (optional): Select from predefined age ranges (16-17, 18-24, 26-44, 45-64, 65+)
   - **Employment Rate** (optional): Percentage of full-time employment (0-100%)
   - **Remote Work Rate** (optional): Percentage of time working remotely (0-100%)
   - **Company Vehicle** (optional): Toggle to indicate if participant has access to a company vehicle
4. Click "Save" to add the participant

**Important:** The identifier field references your company's own participant registry system. Only enter identifiers that exist in your internal system to ensure proper tracking and data privacy.

### Participant Information

Each participant entry in the table displays:

- **Identifier**: The unique identifier referencing your external participant registry
- **Token**: A unique access token generated for this participant
- **Status**: Current participation status (e.g., open, completed)
- **Actions**: Edit or delete buttons for managing the participant

### Accessing the Survey

Each participant is assigned a unique **token** that provides access to the survey:

1. The token appears in the participants table
2. Click on the token to open the survey link in a new tab
3. Use the copy button next to the token to copy the survey URL to clipboard
4. Share this unique link with the participant through your company's preferred communication channel

**Survey URL format:** `https://collect.example.com/go/{token}`

**Important:**

- Each token is unique and should only be shared with the corresponding participant
- Tokens do not expire but become invalid once the campaign ends
- Participants can use the same token to access and complete their survey multiple times until submission

### Managing Participants

#### Editing Participants

To update participant information:

1. Click the edit button (pencil icon) next to the participant
2. Modify the participant details:
   - Identifier (cannot be changed if survey is started)
   - Age class
   - Employment rate
   - Remote work rate
   - Company vehicle status
3. Click "Save" to update the participant

#### Removing Participants

To remove a participant from a campaign:

1. Select the participant(s) to remove
2. Click "Remove Participant"
3. Confirm the removal

**Important:**

- Removed participants can no longer access the survey
- Any in-progress or completed survey data is retained
- Participants can be re-added later if needed

### Participant Status

Participants can have different statuses throughout the campaign:

- **Open**: Participant has not yet accessed the survey or survey started but not completed
- **Completed**: Survey successfully submitted

### Exporting Participant Data

To export participant information:

1. Click "Download CSV" in the participants section
2. A CSV file is automatically generated containing:
   - Identifier
   - Token
   - Survey URL
   - Status
   - Age class
   - Employment rate
   - Remote work rate
   - Company vehicle status
   - Creation date
   - Last update date

**Export uses:**

- Sharing survey links with participants
- Progress tracking and reporting
- Follow-up with non-responders
- Integration with internal systems
- Campaign analytics

### Communication with Participants

#### Campaign-Level Communication

All participant communications use the contact information defined in the campaign settings:

- If campaign-specific contact information is set, participants contact that person
- If not set, the company-level contact information is used
- This ensures participants always have a point of contact for questions

## Best Practices

### When Adding Participants

1. **Use accurate identifiers**: Ensure identifiers match your internal participant registry
2. **Provide complete demographic data**: Optional fields help improve survey analytics
3. **Add participants before campaign start**: Have the complete list ready
4. **Maintain identifier consistency**: Use the same format across all campaigns

### When Sharing Survey Links

1. **Protect token confidentiality**: Each token is unique and should only be shared with the corresponding participant
2. **Use secure communication channels**: Send tokens through your company's approved communication methods
3. **Include context**: Explain the campaign purpose when sharing the survey link
4. **Set clear deadlines**: Communicate when the campaign ends

### When Monitoring Progress

1. **Check completion rates regularly**: Monitor throughout the campaign
2. **Follow up on non-responses**: Contact participants who haven't started
3. **Use the search function**: Filter participants by identifier to track specific individuals
4. **Export data for analysis**: Download CSV to analyze participation patterns

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
