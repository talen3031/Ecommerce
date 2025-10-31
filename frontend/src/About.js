import React from "react";
import rawTypeLogo from "./assets/rawtype-logo.png";
const skills = [
  "街舞", "Python", "Flask", "PostgreSQL", "Docker",  "popping", "Funk","React.js","CI/CD"
];

function About() {
  return (
    <div style={{
      maxWidth: 640,
      margin: "48px auto 0",
      background: "#fff",
      borderRadius: 20,
      boxShadow: "0 8px 32px #0001",
      padding: "40px 32px",
      textAlign: "center"
    }}>
      <img
        src={rawTypeLogo}
        alt="RawType Logo"
        style={{
            width: 120,
            height: 120,
            borderRadius: "50%",
            border: "3px solid #FFD900",
            objectFit: "cover",
            marginBottom: 18,
            background: "#fff"
        }}
        />

      <h1 style={{
        fontSize: "2rem",
        letterSpacing: 2,
        marginBottom: 6,
        color: "#222"
      }}>Welcome to Raw type</h1>
      <div style={{
        color: "#888",
        fontSize: "1.1rem",
        marginBottom: 28
      }}>“Stay Raw. Stay Typed.”</div>
      <div style={{
        fontSize: "1.08rem",
        lineHeight: 2.1,
        textAlign: "left",
        margin: "0 auto 28px",
        maxWidth: 460,
        color: "#444"
      }}>
        There are things we feel but never say.<br />
        Thoughts that stay raw, emotions left unscripted.<br />
        RAWTYPE exists to turn silence into style.<br />
        We take unspoken words and print them loud — on fabric, on street, on skin.<br />
        Expression doesn’t always need a voice.<br />
        Yeah, just wear it.<br />
      </div>
      <div style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 10,
        justifyContent: "center",
        marginBottom: 24
      }}>
        {skills.map(skill => (
          <span key={skill} style={{
            background: "#FFD900",
            color: "#222",
            borderRadius: 14,
            padding: "5px 16px",
            fontWeight: "bold",
            fontSize: "1rem",
            boxShadow: "0 1px 5px #0002",
            letterSpacing: 1
          }}>{skill}</span>
        ))}
      </div>
      <div style={{
        marginTop: 18,
        color: "#444",
        fontSize: "0.98rem"
      }}>
        Contact Email: talen3031@gmail.com
      </div>
    </div>
    
  );
}

export default About;
