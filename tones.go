package main

import (
	"fmt"
	"math/rand"
	"strings"

	MQTT "github.com/eclipse/paho.mqtt.golang"
)

var (
	c MQTT.Client
)

var handler MQTT.MessageHandler = func(client MQTT.Client, msg MQTT.Message) {
	if strings.HasPrefix(msg.Topic(), "interactive_display/touch_events/") {
		/*
			channel, err := strconv.Atoi(msg.Topic()[len("interactive_display/touch_events/"):])
			if err == nil {
				fmt.Println("Got event for channel %d\n", channel)
				for _, toneMap := range data.Tones {
					if toneMap.TouchChannel == channel {
						switch string(msg.Payload()) {
						case "on":
							c.Publish(fmt.Sprintf("interactive_display/audio/note/%d", toneMap.AudioNote), 0, false, strconv.FormatInt(int64(toneMap.Velocity), 10))
							break
						case "off":
							c.Publish(fmt.Sprintf("interactive_display/audio/note/%d", toneMap.AudioNote), 0, false, "off")
							break
						}
					}
				}
			}
		*/
		if string(msg.Payload()) == "on" {
			fmt.Println("Sending random note...")
			note := rand.Intn(85-50) + 50
			c.Publish(fmt.Sprintf("interactive_display/audio/note/%d", note), 0, false, "100")
		}
	}
}

func main() {
	opts := MQTT.NewClientOptions().AddBroker("tcp://localhost:1883")
	opts.SetClientID("tones2")
	opts.SetDefaultPublishHandler(handler)
	c = MQTT.NewClient(opts)
	if token := c.Connect(); token.Wait() && token.Error() != nil {
		panic(token.Error())
	}
	if token := c.Subscribe("interactive_display/touch_events/+", 0, nil); token.Wait() && token.Error() != nil {
		panic(token.Error())
	}
	fmt.Println("Ready.")
	select {}
}
