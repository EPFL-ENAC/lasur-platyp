### Campaign Settings

#### Basic Information

- **Name** (_required_): Campaign identifier
- **Slug**: Unique URL identifier (auto-generated, e.g., "acme-corp-spring-2024-mobility-vx7k")
- **Start Date**: When the campaign begins
- **End Date**: When the campaign closes
- **Number of employees**: Allows you to adjust the tracking of questionnaire response rates in the Dashboard

#### Contact Information

Campaigns can override organisation-level contact information:

- **Contact Name**: Campaign-specific contact person
- **Contact Email**: Campaign-specific email address
- **Information URL**: Campaign-specific information link

If these fields are left empty, the campaign will use the organisation's contact information.


#### Campaign-Specific Measures

If measures to support staff mobility are already in place at the time of the campaign, you can enter details here so that the staff concerned can access this information:

1. Toggle "With employer measures specific to this campaign"
2. Select measures specific to this campaign
3. This is useful for:
   - Pilot programs testing new initiatives
   - Seasonal measures
   - Location-specific measures
   - Limited-time benefits

#### Workplaces

Campaigns must define how workplace locations are handled:

**Open Workplaces:**

- If enabled, participants can enter any workplace address when completing the survey
- Useful for companies with many locations or flexible work arrangements

**Defined Workplaces:**

- Create a list of specific workplace locations
- Each workplace requires:
  - **Name**: Identifier for the workplace (e.g., "Logistic Hub 12", "Downtown Office")
  - **Address**: Full street address
  - **Coordinates**: Latitude and longitude (auto-filled when address is validated)
- Participants select from this list during the survey

**Important:** At least one of these options must be configured:

- Either enable "Open workplaces", OR
- Define at least one specific workplace location

**Bulk Import:**

- Upload a CSV file to add multiple workplaces at once
- Required CSV columns: name, address, lat, lon
- Use the "Upload CSV" button in the workplaces tab
