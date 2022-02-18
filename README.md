# tap-appsflyer

This is a [Singer](https://singer.io) tap that produces JSON-formatted 
data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:
- Pulls raw data from AppFlyer's [Raw Data Reports V5 API](https://support.appsflyer.com/hc/en-us/articles/208387843-Raw-Data-Reports-V5-)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

---
This is a meltano compatible tap and can be configured as below:

- name: tap-appsflyer
    namespace: tap_appsflyer
    pip_url: git+https://github.com/Atif8Ted/tap-appsflyer.git
    executable: tap-appsflyer
    capabilities:
    - catalog
    - discover
    - state
    settings:
    - name: app_id
      kind: string
      description: App ID from which reports are to be loaded.
    - name: api_token
      kind: string
      description: API token generated via your appsflyer admin account.
    - name: start_date
      kind: date_iso8601
      description: the date-time from which you want to start your report.
    - name: reports
      kind: object
      description: the list of reports that you need to pull.
    config:
      app_id: app_id
      api_token: api_token
      start_date: 2022-02-15T14:30:0Z 
      reports: list of reports that you want to pull


### Reports included 
* installs
* installs_retargeting
* organic_installs
* in_app_events
* in_app_events_retargeting
* organic_in_app_events
* uninstalls
* organic_uninstalls
* ad_revenue
* organic_ad_revenue
* ad_revenue_retargeting
