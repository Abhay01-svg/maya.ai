package com.maya.services;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;

@SpringBootApplication
@RestController
@RequestMapping("/api")
public class VoiceServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(VoiceServiceApplication.class, args);
    }

    @PostMapping("/log")
    public String logVoiceTransaction(@RequestBody VoiceTransaction tx) {
        System.out.println("Java Service Logging: User said '" + tx.getText() + "' and Maya replied '" + tx.getReply() + "'");
        // Here you would add high-performance logic, database persistence, or enterprise integration
        return "Logged successfully";
    }
}

class VoiceTransaction {
    private String text;
    private String reply;
    // Getters and Setters
    public String getText() { return text; }
    public void setText(String text) { this.text = text; }
    public String getReply() { return reply; }
    public void setReply(String reply) { this.reply = reply; }
}
