# tap-appsflyer

This is a [Singer](https://singer.io) tap that produces JSON-formatted 
data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:
- Pulls raw data from AppFlyer's [Raw Data Reports V5 API](https://support.appsflyer.com/hc/en-us/articles/208387843-Raw-Data-Reports-V5-)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

---

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
