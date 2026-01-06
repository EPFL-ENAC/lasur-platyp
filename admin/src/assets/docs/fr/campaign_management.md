## Campaign Management

Campaigns are time-bound mobility surveys or initiatives within a company. Each company can have multiple campaigns.

### Campaign Settings

#### Basic Information

- **Name** (_required_): Campaign identifier
- **Description**: Overview of the campaign purpose
- **Start Date**: When the campaign begins
- **End Date**: When the campaign closes
- **Slug**: Unique URL identifier (auto-generated, e.g., "acme-corp-spring-2024-mobility-vx7k")

#### Contact Information

Campaigns can override company-level contact information:

- **Contact Name**: Campaign-specific contact person
- **Contact Email**: Campaign-specific email address
- **Information URL**: Campaign-specific information link

If these fields are left empty, the campaign will use the company's contact information.

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

#### Campaign-Specific Measures

By default, campaigns inherit the employer measures defined at the company level. However, you can enable campaign-specific measures:

1. Toggle "With employer measures specific to this campaign"
2. Select measures specific to this campaign
3. This is useful for:
   - Pilot programs testing new initiatives
   - Seasonal measures
   - Location-specific measures
   - Limited-time benefits

## Best Practices

### When Configuring Measures

1. **Review measures regularly**: Update as new initiatives launch or old ones end
2. **Consider both personal and professional travel**: Many companies focus on commuting but professional travel is equally important
3. **Be specific with custom measures**: Clear, descriptive labels help participants understand available options

### When Setting Up Campaigns

1. **Choose meaningful names**: Include the year or season for clarity
2. **Set realistic end dates**: Allow sufficient time for participation
3. **Define workplaces carefully**: Accurate locations enable better travel time and emissions calculations
4. **Consider campaign-specific measures**: Use them to test new initiatives before company-wide rollout

## Common Issues and Solutions

### "Location is required, make sure address is valid"

**Problem:** Workplace address cannot be validated
**Solution:**

- Ensure the address is complete and accurate
- Try a more specific address format
- Verify coordinates are being populated

### "At least one workplace must be defined for the campaign"

**Problem:** Campaign has no workplace configuration
**Solution:**

- Either enable "Open workplaces", OR
- Add at least one workplace with a valid address

### Custom measures not appearing

**Problem:** Custom measure was created but doesn't show in dropdowns
**Solution:**

- Refresh the company editor
- Verify the measure has labels in both languages
- Check that the correct group was selected
