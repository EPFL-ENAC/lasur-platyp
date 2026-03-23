### Adding Participants

Participants are added manually through the campaign's participants section:

1. Navigate to the campaign's participants section
2. Click "Add" button
3. Enter the participant information:
   - **Identifier** (_required_): A unique identifier that references your organisation's external participant registry (e.g., collaborator ID, badge number)
   - **Age Class** (optional): Select from predefined age ranges (16-17, 18-24, 26-44, 45-64, 65+)
   - **Employment Rate** (optional): Percentage of full-time employment (0-100%)
   - **Remote Work Rate** (optional): Percentage of time working remotely (0-100%)
   - **Company Vehicle** (optional): Toggle to indicate if participant has access to a company vehicle
4. Click "Save" to add the participant

**Important:** The identifier field references your organisation's own participant registry system. Only enter identifiers that exist in your internal system to ensure proper tracking and data privacy.

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
4. Share this unique link with the participant through your organisation's preferred communication channel

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
- If not set, the organisation-level contact information is used
- This ensures participants always have a point of contact for questions
