// src/components/HeroBanner.js
import '@fontsource/luckiest-guy';

export default function HeroBanner() {
  return (
   <div style={{
        background:  'linear-gradient(135deg, #090909ff 0%, #0d0d0dff 100%)',
        padding: '50px 0 30px',
        textAlign: 'center',
        color: 'white',
        position: 'relative',
        overflow: 'hidden'
      }}>
        
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.05"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat'
        }} />
        <div style={{
          position: 'relative',
          zIndex: 1,
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 20px'
        }}>
         <h1 style={{
          fontFamily: "'Bangers', cursive",
          color: "#FFD900",
          fontSize: "clamp(4rem, 6vw, 4rem)",
          letterSpacing: "-0.02em",
          margin: 0,
          textShadow: `
            -3px -3px 0 #E0341B,
            2px -2px 0 #E0341B,
            -2px  2px 0 #E0341B,
            2px  2px 0 #E0341B,
            0px  3px 0 #E0341B,
            0px -3px 0 #E0341B
          `
        }}>
          Nerd.com
            </h1>
        </div>
      </div>

  );
}
