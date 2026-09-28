export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Redirect all direct *.pages.dev traffic to authoritative custom domain
    if (url.hostname.endsWith('.pages.dev')) {
      return Response.redirect(`https://gvsm.dondlingergc.com${url.pathname}${url.search}`, 301);
    }

    // Redirect legacy /web/ path to root /
    if (url.pathname === '/web' || url.pathname === '/web/' || url.pathname === '/web/index.html') {
      return Response.redirect(`https://gvsm.dondlingergc.com/`, 301);
    }

    // Serve static assets normally on gvsm.dondlingergc.com
    return env.ASSETS.fetch(request);
  }
};
