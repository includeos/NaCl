#include <iostream>
#include <net/inet4>
#include <net/ip4/cidr.hpp>
#include <plugins/nacl.hpp>

using namespace net;

std::shared_ptr<Conntrack> nacl_ct_obj;

namespace custom_made_classes_from_nacl {

class My_Filter : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if ((ip4::Cidr{143,23,5,12,24}.contains(pckt.ip_src()) or ip4::Cidr{120,32,34,102,32}.contains(pckt.ip_src()) or ip4::Cidr{34,53,42,40,24}.contains(pckt.ip_src()) or pckt.ip_src() == IP4::addr{10,0,0,20})) {
std::cout << "Accepting\n";
return Filter_verdict::ACCEPT;
}
std::cout << "Dropping\n";
return Filter_verdict::DROP;

	}
};

} //< namespace custom_made_classes_from_nacl

void register_plugin_nacl() {
	INFO("NaCl", "Registering NaCl plugin");

	auto& eth0 = Inet4::stack<0>();
	eth0.network_config(IP4::addr{10,0,0,50}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1});

	custom_made_classes_from_nacl::My_Filter my_filter;

	eth0.ip_obj().input_chain().chain.push_back(my_filter);

	// Ct

	nacl_ct_obj = std::make_shared<Conntrack>();

	INFO("NaCl", "Enabling Conntrack on eth0");
	eth0.enable_conntrack(nacl_ct_obj);
}