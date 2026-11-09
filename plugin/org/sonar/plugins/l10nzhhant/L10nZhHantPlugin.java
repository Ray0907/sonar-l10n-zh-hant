package org.sonar.plugins.l10nzhhant;

import java.util.Collections;
import org.sonar.api.Plugin;

public final class L10nZhHantPlugin implements Plugin {

	@Override
	public void define(Context context) {
		context.addExtensions(Collections.emptyList());
	}
}
