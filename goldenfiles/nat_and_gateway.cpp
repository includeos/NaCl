#include <iostream>
#include <net/inet4>
#include <net/ip4/cidr.hpp>
#include <plugins/nacl.hpp>
#include <net/nat/napt.hpp>
#include <net/router.hpp>

using namespace net;

std::unique_ptr<Router<IP4>> nacl_router_obj;
std::shared_ptr<Conntrack> nacl_ct_obj;
std::unique_ptr<nat::NAPT> nacl_natty_obj;

namespace custom_made_classes_from_nacl {

class Natting : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (pckt.ip_protocol() == Protocol::TCP) {
auto& tcp_pckt = static_cast<tcp::Packet&>(pckt);

if (tcp_pckt.dst_port() == 1500) {
nacl_natty_obj->dnat(pckt, ct_entry, {IP4::addr{10,10,10,50}, 1500});
return Filter_verdict::ACCEPT;
}
}

		// At the end of a Nat we want to accept the packet that hasn't been DNATed or SNATed
		return Filter_verdict::ACCEPT;
	}
};

} //< namespace custom_made_classes_from_nacl

void register_plugin_nacl() {
	INFO("NaCl", "Registering NaCl plugin");

	auto& eth1 = Inet4::stack<1>();
	eth1.network_config(IP4::addr{10,10,10,50}, IP4::addr{255,255,255,0}, 0);
	auto& eth0 = Inet4::stack<0>();
	eth0.network_config(IP4::addr{10,0,0,45}, IP4::addr{255,255,255,0}, 0);


	custom_made_classes_from_nacl::Natting natting;

	eth0.ip_obj().prerouting_chain().chain.push_back(natting);

	// Router

	INFO("NaCl", "Setup routing");
	Router<IP4>::Routing_table routing_table {
		{ IP4::addr{10,0,0,0}, IP4::addr{255,255,255,0}, 0, eth0, 1 },
		{ IP4::addr{10,10,10,0}, IP4::addr{255,255,255,0}, 0, eth1, 1 },
		{ IP4::addr{0,0,0,0}, IP4::addr{0,0,0,0}, IP4::addr{10,0,0,1}, eth0, 1 }
	};
	nacl_router_obj = std::make_unique<Router<IP4>>(routing_table);
	// Set ip forwarding on every iface mentioned in routing_table
	eth0.set_forward_delg(nacl_router_obj->forward_delg());
	eth1.set_forward_delg(nacl_router_obj->forward_delg());

	// Ct

	nacl_ct_obj = std::make_shared<Conntrack>();

	INFO("NaCl", "Enabling Conntrack on eth0");
	eth0.enable_conntrack(nacl_ct_obj);

	INFO("NaCl", "Enabling Conntrack on eth1");
	eth1.enable_conntrack(nacl_ct_obj);

	// NAT

	nacl_natty_obj = std::make_unique<nat::NAPT>(nacl_ct_obj);

	auto snat_translate = [](IP4::IP_packet& pckt, Inet<IP4>&, Conntrack::Entry_ptr entry)-> auto {
		nacl_natty_obj->snat(pckt, entry);
		return Filter_verdict::ACCEPT;
	};
	eth0.ip_obj().postrouting_chain().chain.push_back(snat_translate);
}